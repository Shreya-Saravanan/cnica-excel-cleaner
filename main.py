import gradio as gr
import pandas as pd


DEBUG = True
MAX_RESPONDENT_COUNT = 10
MAX_ADDRESS_COUNT = 10


# This function runs whenever someone uploads or changes the Excel file
def excel_file_changed(excel_path):
    if excel_path is None:
        # Calculate how many None values to return: 1 for dataframe + dropdowns for names + dropdowns for addresses
        return [None] * (1 + MAX_RESPONDENT_COUNT + (MAX_RESPONDENT_COUNT * MAX_ADDRESS_COUNT))
    
    excel_data_frame = pd.read_excel(excel_path)

    column_headers = excel_data_frame.columns.to_list()

    # Create empty lists to store all the dropdown UI elements we're about to create
    name_dropdowns = []
    all_address_dropdowns = []
    
    for i in range(MAX_RESPONDENT_COUNT):
        # Create a dropdown menu for selecting the name column for this respondent
        name_dropdown = gr.Dropdown(
            choices=column_headers,  # Fill it with all the Excel column names
            value=column_headers[0]
        )
        name_dropdowns.append(name_dropdown)

        # Now create dropdowns for all possible address fields for this respondent
        for j in range(MAX_ADDRESS_COUNT):
            address_dropdown = gr.Dropdown(
                choices=column_headers,
                value=column_headers[0]
            )
            all_address_dropdowns.append(address_dropdown)

    # Return the dataframe and all the dropdowns we created
    # The * unpacks the lists (turns [a,b,c] into a, b, c)
    return [excel_data_frame, *name_dropdowns, *all_address_dropdowns]


# This function runs when the user moves the "number of respondents" slider
def respondent_slider_changed(respondent_count):
    # Create an empty list to store visibility settings for each tab
    respondent_tabs = []

    for i in range(MAX_RESPONDENT_COUNT):
        # Create a tab, make it visible only if its index is less than the slider value
        respondent_tab = gr.Tab(visible=i < respondent_count)

        respondent_tabs.append(respondent_tab)

    return respondent_tabs


# This function runs when the user moves the "number of addresses" slider
def address_slider_changed(address_count):
    # Create empty list to store visibility settings for address dropdowns
    address_dropdowns = []

    for i in range(MAX_ADDRESS_COUNT):
        # Create a dropdown, visible only if its index is less than the slider value
        address_dropdown = gr.Dropdown(visible=i < address_count)

        address_dropdowns.append(address_dropdown)
    
    return address_dropdowns


# This function runs when user clicks the "Clean" button
def clean_button_clicked(excel_data_frame, respondent_count, *inputs):
    # inputs[0:10] gets the first 10 items (name dropdowns for each respondent)
    name_column_headers = inputs[0:MAX_RESPONDENT_COUNT]
    # inputs[10:20] gets items 10-19 (the slider values for address counts)
    address_header_counts = inputs[MAX_RESPONDENT_COUNT:2*MAX_RESPONDENT_COUNT]
     # Extract all the address column selections
    # inputs[20:] gets everything after index 20 (all address dropdowns)
    all_address_column_headers = inputs[2*MAX_RESPONDENT_COUNT:]


    # Create a dictionary to organize address columns by respondent
    address_column_headers_dict = {}
   
    # Loop through each respondent
    for i in range(MAX_RESPONDENT_COUNT):
        address_column_headers = []

        # Loop through all possible address columns
        for j in range(MAX_ADDRESS_COUNT):
            # Calculate the index in the flat list: respondent i's address j
            address_column_headers.append(all_address_column_headers[i * MAX_ADDRESS_COUNT + j])

        # Store this respondent's address columns in the dictionary
        address_column_headers_dict[i] = address_column_headers


    # Loop through only the number of respondents the user selected
    for i in range(respondent_count):
        # Loop through each row in the Excel data
        # row_index is the row number, row is the actual data
        for row_index, row in excel_data_frame.iterrows():
            # Get the name value from the Excel for this respondent
            # .loc[row, column] gets the value at that position
            respondent = str(excel_data_frame.loc[row_index, name_column_headers[i]])

            # Loop through the address columns this respondent has
            for j in range(0, address_header_counts[i]):
                # Add each address field to the respondent string, separated by comma
                respondent += ", " + str(excel_data_frame.loc[row_index, address_column_headers_dict[i][j]])

            print(respondent)


def test_button_clicked():
    data_frame = pd.read_excel("./Sample Data 1.xlsx")

    column_headers = data_frame.columns.to_list()
    
    name_dropdown_1 = gr.Dropdown(
        choices=column_headers,
        value="BORROWER NAME"
    )

    name_dropdown_2 = gr.Dropdown(
        choices=column_headers,
        value="Co-Applicant 1 Name"
    )
    
    address_dropdown_1 = gr.Dropdown(
        choices=column_headers,
        value="Borrower Address"
    )

    address_dropdown_2 = gr.Dropdown(
        choices=column_headers,
        value="Co-Applicant 1 - Address"
    )

    return [data_frame, 2, name_dropdown_1, name_dropdown_2, 1, 1, address_dropdown_1, address_dropdown_2]

# Create the main Gradio app interface
with gr.Blocks(title="CNICA Excel Cleaner") as app:
    gr.Markdown("# CNICA Excel Cleaner")

    gr.Markdown("### Step 1: Upload Excel File ###")

     # Create a file upload widget
    excel_file = gr.File(
        label="Excel file",
        file_types=[".xlsx", ".xls"]
    )

    # Create a table/grid to display the Excel data
    excel_data_frame = gr.DataFrame(
        label="Excel data",
        headers=[""],
        interactive=False
    )

    gr.Markdown("### Step 2: Select No. of Respondents ###")

    # Create a slider to choose number of respondents
    respondent_slider = gr.Slider(
        label="No. of Respondents",
        minimum=1,
        maximum=MAX_RESPONDENT_COUNT,
        step=1,
        interactive=True
    )

    gr.Markdown("### Step 3: Select Respondent's Name and Address Column Headers ###")

    # Create empty lists to store all the UI elements we're about to create
    respondent_tabs = []
    name_dropdowns = []
    address_sliders = []
    all_address_dropdowns = []

    # Create a tab for each possible respondent                
    for i in range(MAX_RESPONDENT_COUNT):
        # Create a tab with a label, only first tab visible initially
        with gr.Tab(label=f"Respondent {i + 1}", visible=i==0) as respondent_tab:
            respondent_tabs.append(respondent_tab)

            with gr.Row():
                with gr.Column():
                    # Dropdown to select which column has this respondent's name
                    name_dropdown = gr.Dropdown(
                        label="Name column header",
                        interactive=True
                    )
                    name_dropdowns.append(name_dropdown)

                with gr.Column():
                    # Slider to choose how many address fields this respondent has
                    address_slider = gr.Slider(
                        label="No. of Address column headers",
                        minimum=1,
                        maximum=MAX_ADDRESS_COUNT,
                        step=1,
                        value=1,
                        interactive=True
                    )
                    address_sliders.append(address_slider)
                    
                    # Create empty list for this respondent's address dropdowns
                    address_dropdowns = []

                    # Create all possible address dropdowns
                    for j in range(MAX_ADDRESS_COUNT):
                        address_dropdown = gr.Dropdown(
                            label=f"Address column header {j + 1}",
                            visible=j==0,
                            interactive=True
                        )
                        # Add to local list
                        address_dropdowns.append(address_dropdown)
                        # Also add to the big list of ALL address dropdowns
                        all_address_dropdowns.append(address_dropdown)
                    
                    # Set up event listener: when address slider changes...
                    address_slider.change(
                        fn=address_slider_changed,
                        inputs=address_slider,
                        outputs=address_dropdowns
                    )

    gr.Markdown("### Step 4: Clean Excel File ###")

    # Create the main action button
    clean_button = gr.Button(
        value="Clean",
        variant="primary",
        interactive=True
    )

    # Create a table to show the cleaned results
    cleaned_excel_data_frame = gr.DataFrame(
        label="Cleaned Excel data",
        headers=[""],
        interactive=False
    )

    # Event Listeners

    # When the Excel file changes (uploaded or removed)...
    excel_file.change(
        fn=excel_file_changed,
        inputs=excel_file,
        # Update the dataframe display and all dropdowns
        outputs=[excel_data_frame, *name_dropdowns, *all_address_dropdowns]
    )

    # When the respondent slider changes...
    respondent_slider.change(
        fn=respondent_slider_changed,
        inputs=respondent_slider,
        outputs=respondent_tabs
    )

    # When the clean button is clicked...
    clean_button.click(
        fn=clean_button_clicked,
        # Pass the dataframe, slider value, all name dropdowns, address sliders, and address dropdowns
        inputs=[excel_data_frame, respondent_slider, *name_dropdowns, *address_sliders, *all_address_dropdowns]
    )

    if DEBUG:
        test_button = gr.Button("Test")

        test_button.click(
            fn=test_button_clicked,
            outputs=[excel_data_frame, respondent_slider, 
                    name_dropdowns[0], name_dropdowns[1], 
                    address_sliders[0], address_sliders[1],
                    all_address_dropdowns[0], all_address_dropdowns[10]]
        )

app.launch()
