# Type of Import Config
useAzureTableStorage_config = True
useAzureQueue_config = True # Präsi
isDelta_config = True # Präsi

# More or less standard libs
import os
import time
import sys
import json
import uuid
import pandas as pd
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from typing import Dict
from typing import Union
from typing import Tuple
from typing import List
from pprint import pprint
from typing import Any

# Polaris SDK
import idtbase
import idtims

# Office 365 SDK
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.listitem import ListItem

# Convert integers into 01 format, ensures consistent variable naming
# Never change this, otherwise the whole construct will crash
nf = lambda i: f"{i:02d}"

def next_monday():
    today = datetime.today()
    next_monday = today + timedelta(days=(7 - today.weekday() + 0) % 7)
    return next_monday.date()

def timestamp() -> str:
    """
    Creates current timestamp using GMT+2
    Returns: [HH:MM:SS]
    """
    local_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2)))
    return f"[{local_time.strftime('%H:%M:%S')}]"

def get_absences_from_SharePoint(client_context: ClientContext) -> dict:
    """
    Retrieves absence data from the SharePoint list 'Absences_Input'.

    Args:
        client_context (ClientContext): The SharePoint client context initialized with appropriate credentials.

    Returns:
        dict: A dictionary mapping SharePoint list item IDs to dictionaries containing absence information.
            Each dictionary contains the following keys:
            - 'input_worker_reference_id' (str): The reference ID of the worker associated with the absence.
            - 'input_absence_start' (str): The start date of the absence.
            - 'input_absence_end' (str): The end date of the absence.
            - 'input_absence_worker_comment' (str): Comments provided by the worker regarding the absence.
            - 'input_absence_status' (str): The status of the absence (e.g., Approved, Pending).
            - 'input_absence_created' (str): The date when the absence record was created.
            - 'input_absence_cause' (str): The cause or reason for the absence.

    Example:
        >>> client_context = get_sharepoint_client_context()
        >>> absences = get_absences_from_SharePoint(client_context)
        Example: {
            1: {
                'input_worker_reference_id': 'wr01',
                'input_absence_start': '2024-06-17',
                'input_absence_end': '2024-06-19',
                'input_absence_worker_comment': 'Vacation',
                'input_absence_status': 'Approved',
                'input_absence_created': '2024-06-15',
                'input_absence_cause': 'Holiday'
            },
            2: {
                'input_worker_reference_id': 'wr03',
                'input_absence_start': '2024-06-20',
                'input_absence_end': '2024-06-25',
                'input_absence_worker_comment': 'Sick leave',
                'input_absence_status': 'Pending',
                'input_absence_created': '2024-06-10',
                'input_absence_cause': 'Illness'
            },
            ...
        }
    """
     # Get the SharePoint list 'Absences_Input' rand retrieve items from the list
    large_list = client_context.web.lists.get_by_title("Absences_Input")
    paged_items = (
        large_list.items.paged(1000, page_loaded=print_progress).get().execute_query()
    )
    print(timestamp(), "List fetched: {0}".format(large_list.get().execute_query().title))
    
    # Define SharePoint properties to retrieve
    properties_sp = [
        "Title",
        "input_absence_start",
        "input_absence_end",
        "input_absence_worker_comment",
        "input_absence_status",
        "Created",
        "input_absence_cause"
        ]
    
    properties_for_dict = [
        "input_worker_reference_id",
        "input_absence_start",
        "input_absence_end",
        "input_absence_worker_comment",
        "input_absence_status",
        "input_absence_created",
        "input_absence_cause"
        ]

    # Iterate through each item retrieved from SharePoint
    absence_input_from_sharepoint = {}
    for absence_item in paged_items:
        absence_info = {}

        # Extract specified properties and map them to dictionary keys
        for i in range(len(properties_sp)):
            absence_info[properties_for_dict[i]] = absence_item.get_property(properties_sp[i])

        # Store absence information in the main dictionary using item ID as key
        absence_input_from_sharepoint[absence_item.get_property("ID")] = absence_info
    
    return absence_input_from_sharepoint

def get_worker_skills_data_from_SharePoint(client_context: ClientContext) -> tuple:
    """
    Retrieves worker skills and individual data from the SharePoint list 'User_logins'.

    Args:
        client_context (ClientContext): The SharePoint client context initialized with appropriate credentials.

    Returns:
        tuple: A tuple containing two dictionaries:
            - worker_skills_dict (dict): A dictionary mapping worker titles to tuples of competences.
              Each competence tuple contains (competence_character, 1-based_index).
            - worker_data_dict (dict): A dictionary mapping worker titles to dictionaries of individual data.
              Each dictionary includes 'First_name', 'Last_Name', 'worker_competences', 'Shift_group', and 'Team_Group'.

    Example:
        >>> client_context = get_sharepoint_client_context()
        >>> skills, data = get_worker_skills_data_from_SharePoint(client_context)
        >>> print(data)
        {'wr01': {'First_name': 'John', 'Last_Name': 'Doe', 'worker_competences': 'Sk_A ; Sk_B', 'Shift_group': 'ShiftA', 'Team_Group': 'Team 1'},
         'wr02': {'First_name': 'Jane', 'Last_Name': 'Smith', 'worker_competences': 'Sk_A ; Sk_C', 'Shift_group': 'ShiftB', 'Team_Group': 'Team 2'},
         ...}
        >>> print(data['wr01']['First_name'])
        John
        >>> print(skills)
        {'wr01': (('A', 1), ('B', 2)),
        'wr02': (('A', 1), ('B', 2)),
        'wr03': (('A', 1), ('B', 2)),
        ...
        'wr19': (('B', 1), ('D', 2)),
        'wr20': (('B', 1), ('D', 2))}
        >>> print(skills['wr01'])
        (('A', 1), ('B', 2))
    """
    large_list = client_context.web.lists.get_by_title("User_logins")
    paged_workers = (
        large_list.items.paged(1000, page_loaded=print_progress).get().execute_query()
    )

    print(timestamp(), "List fetched: {0}".format(large_list.get().execute_query().title))

    worker_properties = [
        'Title',
        'First_name',
        'Last_Name',
        'worker_competences',
        "Shift_group",
        'Team_Group'
        ]

    worker_skills_dict = {}
    worker_data_dict = {}
    for worker_item in paged_workers:
        if worker_item.get_property('Title')[:2] == "wr":

            # Extract competences from worker_item property 'worker_competences'
            # Filter out single-character competences and enumerate them
            # This is ugly as hell (sorry) but can be replaced if a more uniform SharePoint list were created
            split_worker_competences = [s[-1] for s in worker_item.get_property('worker_competences').split() if len(s) > 1]
            worker_skills_tuple = tuple([(sk, i+1) for i,sk in enumerate(split_worker_competences)])
            worker_skills_dict[f"{worker_item.get_property('Title')}"] = worker_skills_tuple

            worker_individual_data = {}
            for worker_property in worker_properties[1:]:
                worker_individual_data[worker_property] = worker_item.get_property(worker_property)

            # Store worker data in the main dictionary
            worker_data_dict[f"{worker_item.get_property('Title')}"] = worker_individual_data

    return worker_skills_dict, worker_data_dict

def get_operations_from_SharePoint(client_context: ClientContext) -> dict:
    """
    Retrieves operations data from the SharePoint list 'operations_definitions'.

    Args:
        client_context (ClientContext): The SharePoint client context initialized with appropriate credentials.

    Returns:
        dict: A dictionary mapping operation numbers to dictionaries containing operation information.
              Each dictionary includes the following keys:
              - 'name' (str): The name of the operation.
              - 'station' (str): The station where the operation takes place.
              - 'required_skill' (str): The required skill for the operation.
              - 'machine_time_min' (float): The minimum machine time required for the operation (in minutes).
              - 'personnel_time_min' (float): The minimum personnel time required for the operation (in minutes).
              - 'min_workers' (int): The minimum number of workers required for the operation.
              - 'required_workers' (int): The exact number of workers required for the operation.

    Example:
        >>> client_context = get_sharepoint_client_context()
        >>> operations = get_operations_SP(client_context)
        >>> print(operations['001'])
        {'name': 'Operation of Cutting Machine', 'station': 'cutting_machine_01', 'required_skill': 'B',
         'machine_time_min': 60.0, 'personnel_time_min': 30.0, 'min_workers': 2, 'required_workers': 3}
    """
    large_list = client_context.web.lists.get_by_title("operations_definitions")
    paged_items = (
        large_list.items.paged(1000, page_loaded=print_progress).get().execute_query()
    )
    print(timestamp(),"List fetched: {0}".format(large_list.get().execute_query().title))
    
    properties_sp = [
        "op_name",
        "op_station",
        "op_required_skill",
        "op_machine_time_min",
        "op_personnel_time_min",
        "op_min_workers",
        "op_required_workers"
        ]

    # Iterate through each operation retrieved from SharePoint
    operations_dict = {}
    for operation_number, operation_data in enumerate(paged_items):
        operation_info = {}

        # Extract specified properties and map them to dictionary keys
        for i in range(len(properties_sp)):
            operation_info[properties_sp[i][3:]] = operation_data.get_property(properties_sp[i])

        # Store operation information in the main dictionary using formatted operation number
        operations_dict[f"{nf(operation_number+1)}"] = operation_info

    return operations_dict

def pprint_IDT_values(allRows_type_dictionary: dict, focus_values: list = False) -> print:
    """
    Pretty prints values from the given dictionary of rows with optional focus on specific types.

    Args:
        allRows_type_dictionary (dict): The allRows dictionary as created by the idtbase functionalities.
        focus_values (list, optional): If provided, only prints values for types listed in focus_values.
                                       Defaults to False.

    Returns:
        None
    """

    # If no focus values are specified
    if focus_values:

        static_focus_values = [
        # 'IdtShiftSchedule',
        'IdtShiftScheduleAbsence',
        # 'IdtShiftScheduleShift',
        # 'IdtWorkerResource',
        # 'IdtWorkerPersonnelLink',
        # 'IdtWorkerResource',
        # 'IdtPersonnelResource'
        ]
        
        for key, values in allRows_type_dictionary.items():
            if (len(values) > 0) and (key in static_focus_values):
                print("\n", key)
                for item in values:
                    pprint(item.Values)

    else:
        for key, values in allRows_type_dictionary.items():
            if len(values) > 0:
                print("\n", key)
                for item in values:
                    pprint(item.Values)
    print("\n")

def get_json_data(connection: str, connection_param: str) -> Union[dict, None]:
    """
    Retrieves nested data from a JSON file based on connection type and parameter.

    Args:
        connection (str): The type of connection ('sp' for SharePoint or 'tablestorage' for Table Storage).
        connection_param (str): The parameter path in dot notation to fetch from the JSON file.

    Returns:
        dict or None: If successful, returns the nested data fetched from the JSON file.
                      Returns None in case of errors (FileNotFoundError, JSONDecodeError, KeyError).

    Example:
        >>> data = get_json_data('sp', 'settings.sharepoint.credentials')
        >>> print(data)
        {'username': 'admin', 'password': 'abc123'}
    """
    file_path = os.path.join(
        r"temp", r"sharepoint-settings.json"
        ) if connection == r"sp" else os.path.join(
            r"temp", r"tablestorage-settings.json"
            )
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            keys = connection_param.split('.')
            for key in keys:
                data = data[key]
            # print(data)
            return data

    except FileNotFoundError:
        print("File not found.")
        return False
    
    except json.JSONDecodeError:
        print("Invalid JSON format.")
        return False
    
    except KeyError:
        print("Key not found in JSON.")
        return False

def pprint_sp_list(paged_items: list, properties: list) -> None:
    """
    Pretty prints a SharePoint list or paged items with specified properties.

    Args:
        paged_items (list): A list of items or paged items from SharePoint.
        properties (list): A list of property names to display for each item.

    Returns:
        None

    Example:
        >>> properties = ['Title', 'Created', 'Modified']
        >>> pprint_sp_list(paged_items, properties)
              Title                   Created                Modified
        ------------------------------------------------------------
        0     Item 1                  2023-01-01T12:00:00Z   2023-01-01T14:00:00Z
        1     Item 2                  2023-01-02T08:00:00Z   2023-01-02T10:00:00Z
    """

    # Calculate the maximum width for each column
    column_widths = {p: len(p) for p in properties}
    
    for item in paged_items:
        for p in properties:
            column_widths[p] = max(column_widths[p], len(str(item.get_property(p))))
    
    # Prepare and print the header row
    header_row = " "*10  # For the index column
    for p in properties:
        header_row += p + " " * (column_widths[p] - len(p) + 2)  # Add extra spaces for readability
    print(header_row)
    print("-"*(10 + sum(column_widths[p] + 2 for p in properties)))

    # Print the data rows
    for index, item in enumerate(paged_items):
        print_row = f"{index}{' '*(10-len(str(index)))}"  # Index column
        for p in properties:
            cell_value = str(item.get_property(p))
            print_row += cell_value + " " * (column_widths[p] - len(cell_value) + 2)
        print(print_row)
    print("\n")

def transform_date_format(input_date: str) -> str:
    """
    Converts a UTC date string to a local date string in a specific format.
    Also adapts the 2 hour delta caused by SharePoint server location.
    This output format is adapted for Polaris input.
    
    Args:
        input_date (str): The date string in UTC format, e.g., '2023-06-12T14:00:00Z'.
    
    Returns:
        str: The converted date string in local time, formatted as 'YYYY-MM-DD HH:MM:SS'. 
    """

    utc_datetime = datetime.strptime(input_date, '%Y-%m-%dT%H:%M:%SZ')
    local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=2)))

    return local_datetime.strftime("%Y-%m-%d %H:%M:%S")

def print_progress(items: ListItemCollection) -> None:
    print(timestamp(),"Items read: {0}".format(len(items)))

def push_allRows_to_TableStorage(uri: str, token: str, key: str, allRows: list) -> None:
    """
    Pushes all rows of data to Azure Table Storage after clearing the old partition.

    Args:
        uri (str): The URI of the Azure Table Storage.
        token (str): The authentication token for accessing Azure Table Storage.
        key (str): The key required for authentication.
        allRows (list): A list containing all rows of data to be pushed to Table Storage.

    Returns:
        None
    """

    # Clean up old content
    print(f"[{timestamp()}] Clearing TabelStorage partition ...")
    idtbase.deleteAzureTablestoragePartition(uri, token, key)
    print(f"[{timestamp()}] Old Partition Content Cleared \n")

    # Write new content
    print(f"[{timestamp()}] Writing IDT to TabelStorage partition ...")
    idtbase.writeToAzureTablestorage(uri,token,key,allRows)
    print(f"[{timestamp()}] TableStorage push completed \n")

def get_list_lengths(ctx: ClientContext) -> Tuple[int, int]:
    """
    Retrieves the lengths of two specific lists from SharePoint.

    Args:
        ctx (ClientContext): The client context object for SharePoint connection.

    Returns:
        Tuple[int, int]: A tuple containing the length of 'Absences_Input' list and 'shift_change_1' list.
        current_number_absences, current_number_shift_change_requests
    """
    list_absences = ctx.web.lists.get_by_title("Absences_Input")
    absences_items = list_absences.items.get().execute_query()

    sp_list_shift_change_request = ctx.web.lists.get_by_title("shift_change_1")
    shift_change_request_items = sp_list_shift_change_request.items.get().execute_query()

    current_number_absences = len(absences_items)
    current_number_shift_change_requests = len(shift_change_request_items)

    return current_number_absences, current_number_shift_change_requests

def shift_swap_check_execute_notify(ctx: ClientContext) -> None:
    # for troubleshooting: df[['Title','ws_shift_start','shift_model']]
    """
    Checks and executes shift swaps in SharePoint lists, and notifies relevant parties.

    Args:
        ctx (ClientContext): The client context object for SharePoint connection.

    Returns:
        None

    Notes:
        - Assumes existence of SharePoint lists 'Worker_Shifts_1', 'shift_change_1', and 'notifications'.
        - Performs checks and updates on shift change requests based on certain conditions.
        - Updates shift models and notifies workers and management about successful shift swaps.
    """
    # Retrieve Worker_Shifts_1 list data
    sp_list_worker = ctx.web.lists.get_by_title("Worker_Shifts_1")
    items = sp_list_worker.items.get().execute_query()

    # Create DataFrame for Worker_Shifts_1 data
    worker_shifts_1_df = pd.DataFrame([item.properties for item in items])

    # Retrieve shift_change_1 list data
    sp_list_shifts = ctx.web.lists.get_by_title("shift_change_1")
    items = sp_list_shifts.items.get().execute_query()

    # Create DataFrame for shift_change_1 data
    shift_change_1_df = pd.DataFrame([item.properties for item in items])

    # Fill missing 'ws_shift_start' values in shift_change_1_df from worker_shifts_1_df
    for index, row in shift_change_1_df.iterrows():
        if pd.isnull(row["ws_shift_start"]):
            unique_shift_id = row["Title"]
            worker_row = worker_shifts_1_df.loc[worker_shifts_1_df["unique_shift_id"] == unique_shift_id]
            shift_change_1_df.at[index, "ws_shift_start"] = worker_row["ws_shift_start"].values[0]
            
    # Filter shift_change_1_df where change is not approved yet
    shift_change_1_df = shift_change_1_df[shift_change_1_df['change_approved'] != True]
    grouped_shift_change_1_df = shift_change_1_df.groupby('ws_shift_start')

    # Group by 'ws_shift_start' and check for conflicting shift models
    unique_shift_id_list = []
    for _, shift_group in grouped_shift_change_1_df:

        shift_models = shift_group['shift_model'].unique() # [early,late]

        if len(shift_models) > 1:
            early_shift_id = shift_group[shift_group['shift_model'] == 'early']['Title'].values[0]
            late_shift_id = shift_group[shift_group['shift_model'] == 'late']['Title'].values[0]
            unique_shift_id_list.append(early_shift_id)
            unique_shift_id_list.append(late_shift_id)
            # break
        else:
            print(timestamp(),"No records found with the same 'ws_shift_start' value and different 'shift_model' values.")
            # break

    # Approve shift changes and update shift models in shift_change_1_df
    for index, row in shift_change_1_df.iterrows():
        if row["Title"] in unique_shift_id_list:
            shift_change_1_df.at[index, "change_approved"] = True
            if row["shift_model"] == "early":
                shift_change_1_df.at[index, "shift_model"] = "late"
            elif row["shift_model"] == "late":
                shift_change_1_df.at[index, "shift_model"] = "early"
                
    # Update SharePoint items in shift_change_1 with approved changes
    for index, row in shift_change_1_df.iterrows():
        item = sp_list_shifts.items.get_by_id(row["ID"])
        item.set_property('change_approved', row["change_approved"])
        item.set_property('shift_model', row["shift_model"])
        item.update()
        ctx.execute_query()

    # Retrieve Worker_Shifts_1 list data again
    sp_list_worker = ctx.web.lists.get_by_title("Worker_Shifts_1")

    # Perform shift model updates and notify workers and management
    if len(unique_shift_id_list)>0:

        # We have no idea what's going on here and why it works
        items = sp_list_worker.items.filter(
            "unique_shift_id eq '" + unique_shift_id_list[0] + "' or unique_shift_id eq '" + unique_shift_id_list[1] + "'"
            ).get().execute_query()
        
        print(f"{timestamp()} Entries 'unique_shift_id' {unique_shift_id_list[0]} and {unique_shift_id_list[1]} found.")
        
        for item in items:
            shift_model = item.properties['shift_model']
            if shift_model == 'early':
                item.set_property('shift_model', 'late')
            elif shift_model == 'late':
                item.set_property('shift_model', 'early')
            item.update()
            print(timestamp(),f"Item property {item.properties['unique_shift_id']} was updated to {item.properties['shift_model']}.")
            
        print(timestamp(),'Uploading data...  ')
        ctx.execute_batch()
        print(timestamp(),'Values in "shift_model" updated.')

        # Retrieve notification list
        sp_list_notifications = ctx.web.lists.get_by_title("notifcations")
        items = sp_list_notifications.items.get().execute_query()

        # Notify workers and management about shift swap
        for index, row in shift_change_1_df.iterrows():
            if row["Title"] in unique_shift_id_list:
                title = row["Title"]
                message_wr = f"Changed: You're now in {row['shift_model']} shift in CW{row['Title'][7:11]}"
                sp_list_notifications.add_item({'Title': title[:4], 'message': message_wr})
                ctx.execute_query()
                message_cc = f"Changed: Worker {row['Title'][:4]} to {row['shift_model']} shift in CW{row['Title'][7:11]}"
                sp_list_notifications.add_item({'Title': 'mgmt', 'message': message_cc})
                ctx.execute_query()
                print(timestamp(), f"Shift swap notifications for {title} successfully added!")
    else:
        print(timestamp(),"No suitable shifts for a swap were found.")

def validate_date_delta(absence_properties: Dict[str, str]) -> bool:
    """
    Validates the absence date range based on specified criteria.

    Returns:
        bool: True if the absence reason is "Disease" with attachments, or if the absence end
        date is within 5 days from the creation date. False otherwise.
    """
    if absence_properties['input_absence_reason'] == "Disease":
        return True
    
    else:
        absence_created_datetime = datetime.strptime(absence_properties['Created'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
        absence_end_datetime = datetime.strptime(absence_properties['input_absence_end'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
        return (absence_end_datetime - absence_created_datetime) < timedelta(days=5)

def date_format_for_notifications(absence_properties: Dict[str, str]) -> Tuple[str, str]:
    """
    Converts UTC date strings to local date strings in a specific format for notifications.

    Args:
        absence_properties (Dict[str, str]): Dictionary containing 'input_absence_start' and 'input_absence_end' properties.

    Returns:
        Tuple[str, str]: A tuple containing formatted local date strings for absence start and end times.
    """
    absence_start_datetime_format = datetime.strptime(
        absence_properties['input_absence_start'], "%Y-%m-%dT%H:%M:%SZ"
        ) + timedelta(hours=2)
    absence_end_datetime_format = datetime.strptime(
        absence_properties['input_absence_end'], "%Y-%m-%dT%H:%M:%SZ"
        ) + timedelta(hours=2)

    return absence_start_datetime_format.strftime("%d-%m %H:%M"), absence_end_datetime_format.strftime("%d-%m %H:%M")

def get_current_shifts(client_context: ClientContext) -> Dict[str, str]:
    """
    Retrieve and process current worker shifts from the SharePoint list.

    This function connects to a SharePoint site using the provided client context,
    retrieves the 'worker_shifts_1' list, and processes the data to return a dictionary
    where each key is a formatted string combining the ISO week number and worker title,
    and each value is another dictionary containing the shift model, start date, and end date.

    Args:
        client_context (ClientContext): The client context to connect to the SharePoint site.

    Returns:
        Dict[str, Dict[str, datetime]]: A dictionary with keys as formatted week and worker titles,
                                        and values as dictionaries containing shift model, 
                                        shift start date, and shift end date.

    Example:
        >>> client_context = get_client_context()  # Example of obtaining client context
        >>> get_current_shifts(client_context)
        {
            'cw25_wr01': {
                'shift_model': 'early',
                'shift_start_date': datetime(),
                'shift_end_date': datetime()
            },
            'cw25_wr02': {
                'shift_model': 'late',
                'shift_start_date': datetime(),
                'shift_end_date': datetime()
            },
            ...
            'cw33_wr20': {
                'shift_model': 'late',
                'shift_start_date': datetime(),
                'shift_end_date': datetime()
            }
        }
    """
    # TODO where else is this function used?
    sp_list_worker_shifts = client_context.web.lists.get_by_title("worker_shifts_1")
    items = sp_list_worker_shifts.items.get().execute_query()

    worker_shifts = {}
    for item in items:
        shift_start_date = datetime.strptime(item.get_property("ws_shift_start"), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
        _, iso_week, _ = shift_start_date.isocalendar()
        worker_shifts[f"cw{iso_week}_{item.get_property('Title')}"] = {
            'shift_model': item.get_property("shift_model"),
            'shift_start_date': datetime.strptime(item.get_property("ws_shift_start"), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2),
            'shift_end_date': datetime.strptime(item.get_property("ws_shift_end"), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
            }

    return worker_shifts

def create_shift_model_times(date: datetime, shift_model: str) -> Tuple[datetime, datetime]:
    """
    Create shift start and end times based on the given date and shift model.
    Basically "merges" a given date and the shift times for the worker at this date.

    Args:
        date (datetime): The date for which the shift times need to be created.
        shift_model (str): The shift model, either "early" or "late".

    Returns:
        Tuple[datetime, datetime]: A tuple containing the start and end times of the shift.

    Raises:
        ValueError: If the shift model is not "early" or "late".

    Examples:
        >>> from datetime import datetime
        >>> date = datetime(2024, 6, 22)
        >>> create_shift_model_times(date, "early")
        (datetime.datetime(2024, 6, 22, 7, 0), datetime.datetime(2024, 6, 22, 15, 30))

        >>> create_shift_model_times(date, "late")
        (datetime.datetime(2024, 6, 22, 15, 30), datetime.datetime(2024, 6, 22, 23, 30))
    """

    if shift_model == "early":
        
        shift_start = datetime.combine(date.date(), datetime.strptime("06:00:00", "%H:%M:%S").time())
        shift_end = datetime.combine(date.date(), datetime.strptime("14:00:00", "%H:%M:%S").time())

    elif shift_model == "late":
        shift_start = datetime.combine(date.date(), datetime.strptime("14:00:00", "%H:%M:%S").time())
        shift_end = datetime.combine(date.date(), datetime.strptime("22:00:00", "%H:%M:%S").time())
        
    else:
        print(shift_model, "is no valid input")

    return shift_start, shift_end

def next_weekday(date: datetime) -> datetime:
    next_weekday_date = date + timedelta(days=1)
    
    # If next_date is Saturday (5) or Sunday (6), move to Monday
    if next_weekday_date.weekday() >= 5:
        next_weekday_date += timedelta(days=7 - next_weekday_date.weekday())
    
    return next_weekday_date

def adapt_shift_times_to_next_weekday(worker_shift_dict: dict,
                                      list_item: ListItem,
                                      absence_duration: timedelta) -> tuple:
    """
    Retrieves and calculates the worker's shift model for the next weekday and adjusts absence times.

    Args:
        worker_shift_dict (dict): A dictionary mapping shift model identifiers to shift details.
        list_item (ListItem): A ListItem containing worker properties.
        absence_duration (timedelta): A timedelta object representing the duration of the absence.

    Returns:
        tuple: A tuple containing the adjusted absence start and end times.
    """
    abs_start_datetime = datetime.strptime(list_item.properties["input_absence_start"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
    _, iso_week, _ = next_weekday(abs_start_datetime).isocalendar()
    shift_model_worker_next_weekday = worker_shift_dict[f"cw{iso_week}_{list_item.properties['Title'].lower()}"]['shift_model']
    absence_start_new, absence_end = create_shift_model_times(next_weekday(abs_start_datetime),shift_model_worker_next_weekday)
    if list_item.properties['input_absence_reason'] != "Live-Incident":
        absence_end_new = absence_start_new + absence_duration 
    else:
        absence_end_new = absence_end

    return absence_start_new, absence_end_new

def modify_delay_type_absence(worker_shift_lookup: dict, list_item: ListItem, client_context: ClientContext) -> None:

    abs_start_datetime = datetime.strptime(list_item.properties["input_absence_start"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
    abs_end_datetime = datetime.strptime(list_item.properties["input_absence_end"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
    
    # Delay
    absence_duration = abs_end_datetime-abs_start_datetime

    # Extract encoded time information
    _, iso_week, iso_weekday = abs_start_datetime.isocalendar()

    shift_model_worker_week = worker_shift_lookup[f"cw{iso_week}_{list_item.properties['Title'].lower()}"]['shift_model']
    shift_start_today, shift_end_today = create_shift_model_times(abs_start_datetime, shift_model_worker_week)

    print(timestamp(),f"Original absence: {abs_start_datetime} - {abs_end_datetime} ({abs_start_datetime.weekday()})")

    if abs_start_datetime >= shift_end_today or abs_start_datetime.weekday() >= 5:

        print(timestamp(),"Absence after Feierabend, change to next weekday")

        absence_start_adapted, absence_end_adapted = adapt_shift_times_to_next_weekday(
            worker_shift_lookup,list_item,absence_duration
            )

    # we don't care about tailoring the absence end to the shift end
    # because it will only affect the chosen shift anyway
    elif abs_start_datetime < shift_start_today:
        print(timestamp(),"Absence shortly before the shift, start+end delayed")
        absence_start_adapted = shift_start_today
        absence_end_adapted = (
            shift_start_today + absence_duration
            ) if list_item.properties[
                'input_absence_reason'
                ] != "Live-Incident" else shift_end_today
        
    # abs_start_datetime < shift_end_today:
    else:
        print(timestamp(),"Absence during the shift, no change")
        absence_start_adapted = abs_start_datetime
        # Hammer fell on foot --> rest of shift blocked
        absence_end_adapted = abs_end_datetime if list_item.properties[
            'input_absence_reason'
            ] != "Live-Incident" else shift_end_today

    print(timestamp(),f"Comment: {list_item.get_property('input_absence_worker_comment')}")
    print(timestamp(),f"Adapted absence: {absence_start_adapted} - {absence_end_adapted}\n")

    absence_start_adapted = absence_start_adapted - timedelta(hours=2)
    absence_end_adapted = absence_end_adapted - timedelta(hours=2)

    list_item.set_property('input_absence_start', absence_start_adapted.strftime("%Y-%m-%dT%H:%M:%SZ"))
    list_item.set_property('input_absence_end', absence_end_adapted.strftime("%Y-%m-%dT%H:%M:%SZ"))
    list_item.update()
    client_context.execute_query()
    
    return date_format_for_notifications(list_item.properties)

def date_ranges_overlap(
        start_1: datetime,
        end_1: datetime,
        start_2: datetime,
        end_2: datetime
        ) -> bool:
    """
    Check if two date ranges overlap for at least one minute.

    Args:
        start_1 (datetime): Start of the first date range.
        end_1 (datetime): End of the first date range.
        start_2 (datetime): Start of the second date range.
        end_2 (datetime): End of the second date range.

    Returns:
        bool: True if the two date ranges overlap for at least one minute, False otherwise.
    """
    # Ensure the date ranges overlap
    latest_start = max(start_1, start_2)
    earliest_end = min(end_1, end_2)
    
    # Calculate the overlap duration
    overlap = (earliest_end - latest_start).total_seconds()
    
    # Check if the overlap is at least one minute (60 seconds)
    return overlap >= 60

def count_update_knowledge_availability(
        ctx: ClientContext, workers_skills_info, current_shifts: Dict[str, Any], absence_items: List[Any]
        ) -> None:
    """
    Update the knowledge availability of workers based on their shifts and absences.

    Args:
        ctx (ClientContext): The SharePoint client context.
        workers_skills_info (Dict[str, List[Any]]): Information about workers' skills.
        current_shifts (Dict[str, Any]): Information about current shifts.
        absence_items (List[Any]): List of absence items.

    Returns: 
        None
    """
    
    date_to_check = datetime.now() # datetime(2024, 6, 24, 0, 0)

    # cut out here
    # print("Weekday added: ", date_to_check.weekday())

    # Initialize competence count dictionaries for both regular and actual shifts
    locals()["early_shift_competence_count_regular"] = {
        "A": 0, "B": 0, "C": 0, "D": 0
        }
    locals()["late_shift_competence_count_regular"] = {
        "A": 0, "B": 0, "C": 0, "D": 0
        }
    locals()["early_shift_competence_count_actual"] = {
        "A": 0, "B": 0, "C": 0, "D": 0
        }
    locals()["late_shift_competence_count_actual"] = {
        "A": 0, "B": 0, "C": 0, "D": 0
        }

    # Iterate over each worker and their associated skills
    _, this_iso_week, _ = date_to_check.isocalendar()
    for worker_id, skillset in workers_skills_info.items(): # TODO avoid double counting!

        skill_names = [
            skill_name_prio[0] for skill_name_prio in skillset
            ]

        shift_data = current_shifts[f"cw{this_iso_week}_{worker_id}"]
        shift_model = shift_data['shift_model']

        # Update competence counts for both regular and actual shifts
        for skill_name in skill_names:
            locals()[f'{shift_model}_shift_competence_count_regular'][skill_name] += 1
            locals()[f'{shift_model}_shift_competence_count_actual'][skill_name] += 1
        
        start_shift, end_shift = create_shift_model_times(
            date_to_check, shift_model
            )
        
        # Iterate over each absence item to check for overlaps with current shift
        worker_id_subtracted = False
        for absence_item in absence_items:

            if absence_item.get_property('Title') == worker_id and not worker_id_subtracted:

                start_absence = datetime.strptime(
                        absence_item.get_property('input_absence_start'),
                        "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)

                if start_absence.date() == date_to_check.date():

                    end_absence = datetime.strptime(
                        absence_item.get_property('input_absence_end'),
                        "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)
                    
                    workweek_start = shift_data['shift_start_date']
                    workweek_end = shift_data['shift_end_date']

                    # Check if the absence falls within the workweek
                    is_in_workweek = workweek_start <= date_to_check <= workweek_end
                    if is_in_workweek:
                        overlaps = date_ranges_overlap(
                            start_shift, end_shift, start_absence, end_absence
                            )
                        if overlaps:
                            # Subtract competence counts for overlapping absence
                            for skill_name in skill_names:
                                locals()[
                                    f'{shift_model}_shift_competence_count_actual'
                                    ][skill_name] -= 1
                                
                            # Flag that subtraction has been done
                            worker_id_subtracted = True
                        else:
                            pass # No overlap, do nothing
                    else:
                        pass # Not within workweek, do nothing

    # Update competence availabilities in SharePoint list
    competence_availabilities = ctx.web.lists.get_by_title("Competences_worker")
    competence_items = competence_availabilities.items.get().execute_query()
    for shift_m in ["early","late"]:
        row_data = {}
        row_data["Title"] = shift_m
        row_data['Date_Dia'] = date_to_check.strftime('%Y-%m-%dT%H:%M:%SZ')
        for mode in ['regular','actual']:
            for skill_s in ["A","B","C","D"]:
                row_data[f"comp_{skill_s}_{mode}"] = str(locals()[f'{shift_m}_shift_competence_count_{mode}'][skill_s])

        for competence_item in competence_items:
            date_competence_item = str(
                (datetime.strptime(competence_item.get_property('Date_Dia'),"%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=2)).date()
                )
            date_current_update = str(date_to_check.date())
            date_lookup = date_competence_item==date_current_update
            shift_mode_lookup = competence_item.get_property('Title') == shift_m

            if date_lookup and shift_mode_lookup:
                for key, value in row_data.items():
                    competence_item.set_property(key, value)
                competence_item.update()
                ctx.execute_query()
            else:
                pass

def absence_check_reject_notify(ctx: ClientContext) -> bool:
    """
    Checks absences in Absences_Input SharePoint list, notifies workers, and manages notifications.

    Args:
        ctx: ClientContext object for SharePoint connection.

    Returns:
        bool: True if absence accepted and notifications sent, False if absence rejected and deleted.

    Raises:
        Exception: If there is an issue executing queries or updating items in SharePoint.

    Notes:
        - Uses date_format_for_notifications and validate_date_delta functions for date formatting and validation.
        - Assumes presence of "notifcations" list in SharePoint for notifications.
    """
    contains_live_absence = False
    sp_list_notifications = ctx.web.lists.get_by_title("notifcations")
    worker_shift_dict = get_current_shifts(ctx)

    sp_list = ctx.web.lists.get_by_title("Absences_Input")
    absence_items = sp_list.items.get().execute_query()

    absence_added = False
    for absence_item in absence_items:

        if absence_item.properties["notification_sent"] != True:

            
            worker_ref_id = absence_item.properties['Title']
        
            if absence_item.properties['input_absence_reason'] in ["Delay", "Live-Incident"]:
                start_incident = date_format_for_notifications(absence_item.properties)[0]
                start_date_str, end_date_str = modify_delay_type_absence(worker_shift_dict, absence_item, ctx)
                contains_live_absence = True
            else:
                start_date_str, end_date_str = date_format_for_notifications(absence_item.properties)


            if validate_date_delta(absence_item.properties) and str(worker_ref_id) != "None":
                
                # Accept absence and send positive notification
                
                message_worker = f"Absence added: {start_date_str} - {end_date_str}" if absence_item.properties['input_absence_reason'] != "Live-Incident" else f"Incident reported at {start_incident}"
                sp_list_notifications.add_item({'Title': worker_ref_id, 'message': message_worker})
                ctx.execute_query()

                message_controlcenter = f"Absence added by {worker_ref_id}: {start_date_str} - {end_date_str}" if absence_item.properties['input_absence_reason'] != "Live-Incident" else f"Incident reported by {worker_ref_id} at {start_incident}"
                sp_list_notifications.add_item({'Title': 'mgmt', 'message': message_controlcenter})
                ctx.execute_query()
                print(timestamp(),f"Absence notifications for {worker_ref_id} {start_date_str} - {end_date_str} successfully added!")

                # Setze die Spalte "notification_sent" auf "true" für alle Zeilen im DataFrame
                absence_item.set_property("notification_sent", "true") # it works, but why? True != "true" (!)
                absence_item.update()
                ctx.execute_query()
                print(timestamp(),f"Notification_sent for {worker_ref_id} {start_date_str} -  {end_date_str} updated!")
                absence_added = True
            
            else:    
                # Delete absence and send positive notification
                absence_item.recycle().execute_query()

                message_worker = f"Rejected: Your absence {start_date_str} - {end_date_str}"
                sp_list_notifications.add_item({'Title': worker_ref_id, 'message': message_worker})
                ctx.execute_query()
                print(timestamp(), f"Absence {worker_ref_id} {start_date_str} - {end_date_str} deleted!")

    # It might occure that multiple absence are processed in the the same iteration
    # therefore we must put this here to ensure 1. every absence is considered
    # this doesn't excecute unneccesarily
    if absence_added:
        workers_skills_info, _ = get_worker_skills_data_from_SharePoint(ctx)
        current_shifts = get_current_shifts(ctx)
        count_update_knowledge_availability(ctx,workers_skills_info,current_shifts,absence_items)

    return contains_live_absence

def write_export_upload_IDT(allRows: List[dict], useAzureTableStorage: bool, useAzureQueue: bool, isDelta: bool) -> None:
    """
    Writes the IDT (Integration Data Transfer) data to either an Excel file, Azure Table Storage, or
    Azure Queue based on the provided parameters.

    Parameters:
    - allRows (list): The data rows to be written/exported.
    - useAzureTableStorage (bool): Flag indicating whether to use Azure Table Storage for data storage.
    - useAzureQueue (bool): Flag indicating whether to use Azure Queue for triggering data import.
    - isDelta (bool): Flag indicating whether the operation is a delta import (True) or a full import (False).

    Behavior:
    - If `useAzureTableStorage` is False, the function writes the IDT data to an Excel file named 
      "dynamic_env_overwrite.idt.xlsx" in the "temp" directory.
    - If `useAzureTableStorage` is True:
      - If `useAzureQueue` is True, it reads queue parameters from "sbn_esb.json", pushes the data to Azure 
        Table Storage, and then sends a message to Azure Queue to trigger the import in Polaris.
      - If `useAzureQueue` is False, it reads storage parameters from "tablestorage-settings.json" and pushes 
        the data to Azure Table Storage.

    Exceptions:
    - If the JSON configuration files ("sbn_esb.json" or "tablestorage-settings.json") are not valid or not 
      found, the function prints an error message and exits the program.

    Function documentation created with ChatGPT-4   
    """
    if not useAzureTableStorage:
        idtims.writeIdtToExcel(f"temp\dynamic_env_overwrite.idt.xlsx", allRows)
        print(f"{timestamp()} Written IDT to Excel")

    else:
        # Fill up TableStorage with IDT
        if useAzureQueue:

            # AzureQueue Parameters
            queue_profile = r"temp\sbn_esb.json"
            try:
                with open(queue_profile, newline='') as jsonfile:
                    settings = json.load(jsonfile)
                    
                    queueConnection = settings['QueueConnection']
                    outgoing_queueName = settings['QueueName']
                    imsTenantDatabase = settings['TenantDatabase']
                    imsClientArea = settings['ClientArea']
                    output_uri = settings['TablestorageUri']
                    output_sasToken = settings['SasToken']
                    output_partitionKey = settings['PartitionKey']
                    login = settings['Login']
                    dataset_profile = settings['DatasetProfile']
            except:
                print(f"Json data {queue_profile} not valid not found")
                sys.exit()

            push_allRows_to_TableStorage(output_uri, output_sasToken, output_partitionKey, allRows)
            print(f"{timestamp()} Will start queue setup and execution in 5 seconds ...")
            time.sleep(5) # security delay for correct TableStorage upload
            print(f"{timestamp()} Starting queue setup and execution")
            # Trigger the automatic import
            outgoing_messageData = {}   
            outgoing_messageData["JobId"] = str(uuid.uuid4())

            if isDelta == True:	
                outgoing_messageData["JobType"] = 'idtdeltaimport'
            else:
                outgoing_messageData["JobType"] = 'idtfullimport'

            outgoing_messageData["ImsTenantDatabase"] = imsTenantDatabase
            outgoing_messageData["ImsClientArea"] = imsClientArea
            outgoing_messageData["Login"] = login
            
            ## idt input source
            outgoing_messageData["TablestorageConnection"] = output_uri + output_sasToken
            outgoing_messageData["PartitionKey"] = output_partitionKey
            ## idt>ims storage target
            outgoing_messageData["DatasetProfile"] = dataset_profile

            outgoing_message = json.dumps(outgoing_messageData, indent=4)
            idtbase.sendToAzureQueue(queueConnection, outgoing_queueName, outgoing_message)
            print(f"{timestamp()} Queue executed. Usual delay for Polaris import: 1 minute. Wait 4 Minutes")

        else:
            queue_profile = r"temp\tablestorage-settings.json"
            try:
                with open(queue_profile, newline='') as jsonfile:
                    settings = json.load(jsonfile)

                    output_uri = settings['uri']
                    output_sasToken = settings['sas']
                    output_partitionKey = settings['partition']

            except:
                print(f"Json data {queue_profile} not valid not found")
                sys.exit()
            push_allRows_to_TableStorage(output_uri, output_sasToken, output_partitionKey, allRows) 

def create_IDT(ctx: ClientContext) -> dict:
    """
    Creates and returns the IDT (Integration Data Transfer) data structure as a dictionary.

    Parameters:
    - ctx (ClientContext): Client context object for SharePoint operations.

    Returns:
    - allRows (dict): The complete IDT data structure.

    Behavior:
    - Retrieves absence, worker skills, and operations information from SharePoint using provided context.
    - Constructs the IDT data structure with products, resources, processes, organizational units, workers, absences,
      and other related data.
    """
    absence_dict = get_absences_from_SharePoint(ctx)
    workers_skills_info, worker_data = get_worker_skills_data_from_SharePoint(ctx)
    operations_info = get_operations_from_SharePoint(ctx)
    current_shifts = get_current_shifts(ctx)

    allRows = idtims.createIdtRowMap()
    idgen = idtbase.IIDGenerator()

    # Script Parameters

    startDate = datetime(2023, 10, 16, 7, 0) 
    endDate = datetime(2023, 12, 31, 23, 30)

    # IMD - Products

    p1 = idtbase.addIdtRow(allRows, idtims.Product(idgen, "Product 1"))
    p1confA = idtbase.addIdtRow(allRows, idtims.ProductConfiguration(idgen, "Variant A", p1))
    p1confB = idtbase.addIdtRow(allRows, idtims.ProductConfiguration(idgen, "Variant B", p1))
    p1root = idtbase.addIdtRow(allRows, idtims.Component(idgen, "Root Assembly", p1))

    # IMD - Resources

    # The base shift - we will only use one of these otherwise the code must be adpated to dynamically assign ss{n} !
    # shift_schedule_1 = idtbase.addIdtRow(allRows, idtims.ShiftSchedule(idgen, "1S", "1S"))
    shift_schedule_2S = idtbase.addIdtRow(allRows, idtims.ShiftSchedule(idgen, "2S", "2S"))

    globals()['sss_e'] = idtbase.addIdtRow(allRows, idtims.ShiftScheduleShift(
        idgen, "Early Shift", "E", "Monday", "Friday", "06:00:00", "14:00:00", shift_schedule_2S
        ))
    globals()['sss_e'].ReferenceId = 'ss2_e'
    globals()['sss_l'] = idtbase.addIdtRow(allRows, idtims.ShiftScheduleShift(
        idgen, "Late Shift", "L", "Monday", "Friday", "14:00:00", "22:00:00", shift_schedule_2S
        ))
    globals()['sss_l'].ReferenceId = 'ss2_l'

    # Create ShiftSchedule for workers
    workers_amount = len(worker_data)

    shift_schedules = []

    for i in range(1,workers_amount+1):
        globals()[f"ssw{nf(i)}"] = idtbase.addIdtRow(
            allRows, idtims.ShiftSchedule(
                idgen, f"W{nf(i)} 2S", f"W{nf(i)}", shift_schedule_2S
                ))
        shift_schedules.append(globals()[f"ssw{nf(i)}"])

    # Fill up the SSS with data and assign reference IDs
    for sss in (globals()['sss_e'], globals()['sss_l']):
        for i in range(1,workers_amount+1):
            sss = idtbase.addIdtRow(allRows, idtims.ShiftScheduleShift(
                idgen,
                sss.Values['NAME'],
                sss.Values['IDENT'],
                sss.Values['STARTDAY'],
                sss.Values['ENDDAY'],
                sss.Values['STARTTIME'],
                sss.Values['ENDTIME'],
                globals()[f"ssw{nf(i)}"]
                ))
            sss.ReferenceId = f"ssw{nf(i)}_{sss.Values['IDENT']}"

    # Create stations
    station_list = [m['station'] for m in operations_info.values()]
    station_ids = [int(_id) for _id in list(operations_info.keys())]
    station_names = [m['name'].split("of ", 1)[1] for m in operations_info.values()]
    for i in range(1,len(station_list)+1):
        globals()[f"station{nf(station_ids[i-1])}"] = idtbase.addIdtRow(
            allRows, idtims.Station(
                idgen, station_names[i-1], i, shift_schedule_2S
                ))

    # Create skills
    unique_skills = sorted({s[0] for w in workers_skills_info.values() for s in w})
    for i in range(1,len(unique_skills)+1):
        globals()[f"skill{unique_skills[i-1]}"] = idtbase.addIdtRow(
            allRows, idtims.PersonnelResource(
                idgen, f"Skill {unique_skills[i-1]}", shift_schedule_2S
                ))

    # Create organizational units TODO dynamic lookup from all available team_groups in SharePoint
    org_units = ["Team 1","Team 2"]
    for i in range(1, len(org_units)+1):
        globals()[f"ou{nf(i)}"] = idtbase.addIdtRow(
            allRows, idtims.OrgUnit(
                idgen, org_units[i-1]
                ))

    # Create WORKERS and assign reference IDs
    worker_shift_dict = {} # (worker_ref_id, shift_ref_id, WorkerResource-Object, ShiftSchedule-Object)
    for i, wk in enumerate(worker_data):
        worker_name = worker_data[wk]['First_name'] +' '+ worker_data[wk]['Last_Name']
        worker_org_unit = globals()[f"ou{nf(int(worker_data[wk]['Team_Group'][-1]))}"]
        globals()[list(worker_data.keys())[i]] = idtbase.addIdtRow(
            allRows,idtims.WorkerResource(
                idgen, worker_name, globals()[f"ssw{nf(i+1)}"], worker_org_unit
                ))
        globals()[list(worker_data.keys())[i]].ReferenceId = list(worker_data.keys())[i]

        # Tuple of workers for convenient lookup of connected shifts
        # TODO this worker reference call for the global() is the worst hairball ever
        worker_shift_dict[globals()[f"wr{nf(i+1)}"].ReferenceId] = {
            "worker_object": globals()[f"wr{nf(i+1)}"],
            "shift_object": globals()[f"ssw{nf(i+1)}"]
            }

    worker_personnel_links = []
    for worker_ref_id in workers_skills_info:
        for ws in workers_skills_info[worker_ref_id]:
            worker_personnel_links.append((globals()[f'{worker_ref_id}'],
                                           globals()[f'skill{ws[0]}']))
    for wpl in worker_personnel_links:
        idtbase.addIdtRow(allRows, idtims.WorkerPersonnelLink(idgen, wpl[0], wpl[1], 1))

    # it looks like evey worker needs to have a primary station
    # they should be assigned to logic connections in the sense of skill-station connection in operation later
    skill_station_connectors = {}
    for skill in unique_skills:
        stations_list = []
        for i, st in enumerate(operations_info):
            if operations_info[st]['required_skill'] == skill:
                stations_list.append(st)

        skill_station_connectors[skill] = stations_list
    
    # for wpl in worker_personnel_links:
    worker_station_links = []
    for wr in workers_skills_info:
        for skill in workers_skills_info[wr]:
            for s_id in skill_station_connectors[skill[0]]:
                worker_station_links.append((globals()[wr],globals()[f'station{s_id}']))

    # Create station-worker links
    for wsl in worker_station_links:
        idtbase.addIdtRow(allRows, idtims.WorkerStationLink(idgen, wsl[0], wsl[1],"First"))
    
    # The "opposite absence" logic to work out UC2
    _, this_iso_week, _ = datetime.now().isocalendar()
    for cwXX_wrXX, shift_info in current_shifts.items(): # TODO adapt to current_shifts format
        if int(cwXX_wrXX[2:4]) <= this_iso_week+1:
            wr_ref_id = cwXX_wrXX[-4:]
            # get the correct shift to block
            if shift_info['shift_model'] == 'early':
                start_time, end_time = globals()['sss_l'].Values['STARTTIME'], globals()['sss_l'].Values['ENDTIME']
                shift_ident = 'L'

            elif shift_info['shift_model'] == 'late':
                start_time, end_time = globals()['sss_e'].Values['STARTTIME'], globals()['sss_e'].Values['ENDTIME']
                shift_ident = 'E'
            else:
                print("Something wrong with early/late shift assignment. GLHF")
            
            start_time_format = f"{shift_info['shift_start_date'].strftime('%Y-%m-%d')} {start_time}"
            end_time_format = f"{shift_info['shift_end_date'].strftime('%Y-%m-%d')} {end_time}"

            absence_object = idtbase.addIdtRow(allRows, idtims.ShiftScheduleAbsence(
                idgen,start_time_format,end_time_format,worker_shift_dict[wr_ref_id]['shift_object']
                ))
            
            absence_object.ReferenceId = f"ABS_{wr_ref_id}_2S_{shift_info['shift_start_date'].strftime('%Y-%m-%d')}"

            absence_object.Values['COMMENT'] = "Automatically generated by 2S Workaround"
            absence_object.Values['CAUSE'] = 'Unknown'
            absence_object.Values['STATUS'] = 'Active'
            absence_object.Values['SHIFT_IDENTS'] = shift_ident

    # ------------------------------------------------------------------------

    # Realize absence creation
    if len(absence_dict) > 0:

        cause_keys = {
            "Unknown": "Unknown",
            "Plant holidays": "PlantHolidays",
            "Plant shutdown": "Shutdown",
            "Inventory": "Inventory",
            "Maintenance": "Maintenance",
            "Internal absence": "Internal",
            "External absence": "External"
        }
        # get_worker_skills_data_from_SharePoint(ctx) # TODO DELETE
        # get_absences_from_SharePoint(ctx) # TODO DELETE

        for _ ,absence_data in absence_dict.items():

            try:
                absence_target_shift = worker_shift_dict[absence_data["input_worker_reference_id"].lower()]["shift_object"]

                # Create absence
                start_time = transform_date_format(absence_data['input_absence_start'])
                end_time = transform_date_format(absence_data['input_absence_end'])

                # print("Start ", start_time, " End ", end_time)
                absence_object = idtbase.addIdtRow(
                    allRows, idtims.ShiftScheduleAbsence(
                        idgen, start_time, end_time, absence_target_shift
                        ))
            
                # Fill up the SSS with data and assign reference IDs
                absence_ref_id = f"ABS_{absence_data['input_worker_reference_id'][2:]}_{absence_data['input_absence_created']}"
                absence_object.ReferenceId = absence_ref_id

                # assign values to Columns
                for Column in ['COMMENT','CAUSE','STATUS']:
                    try:
                        if Column == "CAUSE":
                            absence_object.Values[Column] = cause_keys[absence_data[f'input_absence_worker_{Column.lower()}']]
                        else:
                            absence_object.Values[Column] = absence_data[f'input_absence_worker_{Column.lower()}']
                    except KeyError:
                        pass
                print(timestamp(),f"Absence object added for {absence_data['input_worker_reference_id']}!")

            except KeyError:
                print(timestamp(),f"Missing worker data!")
                pass
            
    else:
        pass

    # IMD - Processes 

    rootProcess = idtbase.addIdtRow(
        allRows, idtims.OrganizationalProcess(idgen, "Root", "root", 1)
        )
    
    lineProcess1 = idtbase.addIdtRow(
        allRows, idtims.OrganizationalProcess(idgen, "Production", "line1", 1, rootProcess)
        )

    wp1 = idtbase.addIdtRow(
        allRows, idtims.WorkingPlan(
            idgen, 'WP 1', 'line1_wp1', 1, lineProcess1
            ))

    for i, op in enumerate(operations_info.values()):

        machine_t = (op['machine_time_min'],"min") if op['machine_time_min'] != 0 else None
        personnel_t = (op['personnel_time_min'],"min") if op['personnel_time_min'] != 0 else None
        min_w = op['min_workers'] if op['min_workers'] != 0 else None
        req_w = op['required_workers'] if op['required_workers'] != 0 else None

        globals()[f"op1_{i+1}"] = idtbase.addIdtRow(
            allRows, idtims.Operation(
                idgen,
                f"P{i+1}",
                f"line1_wp1_p{i+1}",
                i+1,
                wp1,
                globals()[f"station{nf(i+1)}"],
                globals()[f"skill{op['required_skill']}"],
                machine_t,
                personnel_t,
                min_w,
                req_w
                ))

    idtbase.addIdtRow(
        allRows, idtims.Precedence(
            idgen,
            globals()["op1_1"],
            globals()["op1_2"]
            ))
    
    idtims.linkOperationsSequential(
        allRows, idgen, (
            globals()["op1_2"],
            globals()["op1_3"],
            globals()["op1_4"],
            globals()["op1_5"],
            globals()["op1_6"]
            ))

    np1 = idtbase.addIdtRow(
        allRows, idtims.NetworkPlan(
            idgen, "NP WP1 Variant A", True
            ))
    
    idtbase.addIdtRow(allRows, idtims.NetworkPlanConfLink(idgen, np1, p1confA))
    for i,p in enumerate(
        (lineProcess1,
         wp1,
         globals()["op1_2"],
         globals()["op1_3"],
         globals()["op1_4"],
         globals()["op1_5"],
         globals()["op1_6"]
         )):
        idtbase.addIdtRow(
            allRows,
            idtims.GanttVertex(
                idgen, np1, p, i
                ))

    ### IMC - structure 
    # No need for changes
    mo1 = idtbase.addIdtRow(allRows, idtims.MasterOrder(idgen, "mo1", "Master order"))
    mo1.PlannedStart = startDate
    mo1.PlannedEnd = endDate

    po1 = idtbase.addIdtRow(
        allRows, idtims.ProductionOrder(idgen, "PO_1", "PO 1", "PO_0010201", mo1, p1confA, np1)
        )
    
    po1.PlannedStart = datetime(2023, 10, 16, 7, 0)
    po1.PlannedEnd = datetime(2023, 10, 19, 15, 0)

    for i, p in enumerate(
        (lineProcess1,
         wp1,
         globals()["op1_2"],
         globals()["op1_3"],
         globals()["op1_4"],
         globals()["op1_5"],
         globals()["op1_6"])):
        oi = idtbase.addIdtRow(allRows, idtims.OrderItem(idgen, po1, p, None, i))

    ra1 = idtbase.addIdtRow(
        allRows, idtims.ResourceAllocation(
            idgen, "ra1", "Resource Allocation 1", "ByWorkerShiftAgnostic", "ByTeam"
            ))
    ra1.PlannedStart = startDate
    ra1.PlannedEnd = endDate

    idtbase.addIdtRow(allRows, idtims.ResourceAllocationOrder(idgen, ra1, po1))

    # IMV - Simulation Parameters

    idtbase.addIdtRow(
        allRows, idtims.SimulationParameter(
            idgen, "$default_shiftschedule", "Default shift schedule", "string", "1S"
            )) # bei Zweischicht 2S 

    return allRows

def main():
    # Init SharePoint context
    print(f"{timestamp()} Connecting to SharePoint ...")

    SP_URL = get_json_data("sp", "siteurl")
    SP_CLIENT_ID = get_json_data("sp","clientid")
    SP_CS = get_json_data("sp","clientsecret")

    client_credentials = ClientCredential(f'{SP_CLIENT_ID}',f'{SP_CS}')
    ctx = ClientContext(f'{SP_URL}').with_credentials(client_credentials)

    if SP_CS:
        print(f"{timestamp()} Connected!\n")
        print(f"{timestamp()} Starting to monitor ESBPowerAPPDataSourceMOMProject SharePoint lists \n")
    else:
        print(f"{timestamp()} SharePoint Connection failed due to issues with JSON retrieval!\n")
        exit()

    # ------------------------ 
    # ARTIFICIAL CRON JOB CODE  
    #
    # CUT HERE FOR CRON JOB DEPLOYMENT
    # REPLACE "while True" and memory_shift_change_requests, memory_absences = 0,0
    #
    # WITH
    # 
    # def main(timer: func.TimerRequest) -> None:
    # Retrieve the environment variables
    # memory_shift_change_requests = int(os.environ.get("SHIFT_SWAP_REQ_NO"))
    # memory_absences = int(os.environ.get("ABSENCES_NO"))
        
    # Update the values
    # current_no_absences, current_no_sc_req = get_list_lengths(ctx)
    # os.environ["SHIFT_SWAP_REQ"] = str(current_no_absences)
    # os.environ["MY_VARIABLE"] = str(current_no_sc_req)
    # ------------------------

    # Define the interval (in seconds) for the artifical CRON job to run
    memory_absences, memory_shift_change_requests  = 0,0
    time_interval = 15 # seconds
    time_interval_upload = 240 # minutes TODO adapt to Queue duration + 1 minute

    i = 0
    while True:
        
        start_time = datetime.now()
            
        current_no_absences, current_no_sc_req = get_list_lengths(ctx) # e.g. (35, 7)

        # First loop does nothing so the numbers initialize properly

        if i != 0:
            if current_no_absences != memory_absences:
                print(timestamp(),"New absences!")
                if absence_check_reject_notify(ctx):
                    # if absence_check_reject_notify returns True: 
                    print(f"{timestamp()} Incident occured. Inmediate action required.")
                    # allRows = create_IDT(ctx)
                    # print(f"{timestamp()} IDT created!")
                    # write_export_upload_IDT(allRows, useAzureTableStorage_config, useAzureQueue_config, isDelta_config)

            else:
                print(timestamp(),"Waiting for new absences...")

            if current_no_sc_req != memory_shift_change_requests:
                print(timestamp(),"New shift swap requests!")
                shift_swap_check_execute_notify(ctx)

            else:
                print(timestamp(),"Waiting for new shift swap requests...")
        else:
            print(timestamp(),"Initialize loop")
            pass
        
        memory_absences = current_no_absences
        memory_shift_change_requests = current_no_sc_req

        if i % int(time_interval_upload/time_interval) == 0 and i != 0:
            print(f"{timestamp()} {time_interval_upload}s have passed. Uploading IDT.")
            print(f"{timestamp()} Creating IDT ...")
            allRows = create_IDT(ctx)
            print(f"{timestamp()} IDT created!")
            write_export_upload_IDT(allRows, useAzureTableStorage_config, useAzureQueue_config, isDelta_config)

        # Loop delay to ensure evenly distributed execution
        end_time = datetime.now().timestamp()
        sleeptime = ((start_time + timedelta(seconds=time_interval)).timestamp() - end_time)
        sleeptime = sleeptime if sleeptime >= 0 else 0
        print(f"     (Execution time: {(datetime.now() - start_time).total_seconds()} seconds)\n")
        time.sleep(sleeptime)
        i += 1

if __name__ == '__main__':
    main()
