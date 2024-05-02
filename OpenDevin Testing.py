import subprocess
from selenium import webdriver
from selenium.webdriver.edge.service import Service  # Import Service from edge.service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import shutil
import os


DIRVER_PATH = 'msedgedriver.exe'
INTERFACE_PATH = "http://localhost:3001/"
TEST_PATH = "Project Task 6 - Eval.xlsx"
OPENDEVIN_DIR = r'E:\College Notes\2024 Spring\11711 Advanced NLP\HW4'
OUTPUT_DIR = r'E:\College Notes\2024 Spring\11711 Advanced NLP\HW4\OpenDevin Output'


def get_test_case(dir=TEST_PATH):
    # Load the spreadsheet
    xlsx = pd.ExcelFile(dir)

    # Read the first sheet (by default sheet_name is 0 which reads the first sheet)
    df = pd.read_excel(xlsx, sheet_name=0)

    # Extracting the columns under the names 'prompt 1', 'prompt 2', and 'prompt 3'
    # Assuming these are the column headers we are looking for
    prompts_df = df[['Test Purpose', 'Prompt 1', 'Prompt 2', 'Prompt 3']]


    # Convert the DataFrame to a list of lists where each row is a sublist
    tests = prompts_df.values.tolist()
    tests = [[str(item) for item in sublist if pd.notna(item)] for sublist in tests]

    return tests


def arrange_files():
    source_dir = OPENDEVIN_DIR
    output_dir = OUTPUT_DIR

    # Function to get creation time of a file
    def get_creation_time(file_path):
        return os.path.getctime(file_path)

    # List all txt files in the source directory and sort them by name
    # Assuming that the naming convention ensures correct order
    txt_files = sorted([f for f in os.listdir(source_dir) if f.startswith('test') and f.endswith('.txt')])

    # Create a dictionary to hold the creation times of each txt file
    creation_times = {}

    # Get creation times of each txt file
    for txt_file in txt_files:
        full_path = os.path.join(source_dir, txt_file)
        creation_times[txt_file] = get_creation_time(full_path)

    # List all files in the output directory
    output_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]

    # Loop through each txt file and create a new directory for it
    for i, txt_file in enumerate(txt_files):
        # Determine the time range based on adjacent txt files
        start_time = creation_times[txt_files[i - 1]] if i > 0 else 0  # Start from the previous file's creation time
        end_time = creation_times[txt_file]  # End at the current file's creation time

        # Folder for the current txt file
        folder_name = os.path.splitext(txt_file)[0]
        new_folder_path = os.path.join(source_dir, folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Copy the current txt file into its folder
        shutil.copy(os.path.join(source_dir, txt_file), new_folder_path)

        # Loop through files in the output directory and copy the relevant ones
        for output_file in output_files:
            output_file_time = get_creation_time(output_file)
            if start_time < output_file_time < end_time:
                shutil.copy(output_file, new_folder_path)


def run_tests(tests, starting_index = 0):

    for idx, test in enumerate(tests):
        if idx < starting_index:
            continue

        # run_commands()

        driver_path = DIRVER_PATH  # Update this to your actual EdgeDriver path
        service = Service(executable_path=driver_path)
        driver = webdriver.Edge(service=service)
        driver.get(INTERFACE_PATH) # Update your localhost address

        test_logs = []

        for task_idx, task in enumerate(test[1:]):
            # Wait for the element to load (using WebDriverWait is the better approach)
            driver.implicitly_wait(15)

            textarea = driver.find_element(By.CSS_SELECTOR, "textarea[aria-label='Message assistant...']")
            text_to_enter = task
            textarea.click()
            textarea.send_keys(text_to_enter)

            time.sleep(10)
            sendbutton = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send message']")
            sendbutton.click()

            finished = False
            task_fail = False
            test_start = time.time()
            all_done_flag = task_idx

            while True:
                try:
                    time.sleep(20)
                    elements = driver.find_elements(By.CLASS_NAME, "p-3")
                    for element in elements:
                        if element.text == "All done! What's next on the agenda?":
                            if all_done_flag == 0:
                                finished = True
                                break
                            else:
                                all_done_flag -= 1
                        if time.time() - test_start > 300:
                            task_fail = True
                            break
                    if finished:
                        break
                    if time.time() - test_start > 300:
                        task_fail = True
                        break
                except:
                    return idx

            all_done_flag = task_idx

            if task_fail:
                task_logs = [f"task failed after {len(elements)} iterations"]
            else:
                task_logs = []

            for element in elements:
                if all_done_flag == 0:
                    task_logs.append(element.text)
                    if element.text == "All done! What's next on the agenda?":
                        break
                else:
                    if element.text == "All done! What's next on the agenda?":
                        all_done_flag -= 1

            test_logs.append(task_logs)

        with open(f'test {idx}.txt', 'w') as file:
            file.write("test type: " + test[0] + '\n')
            for sublist in test_logs:
                # Write each string in the sublist separated by one line
                for string in sublist:
                    file.write(string + '\n')
                # Separate each sublist by three line breaks
                file.write('\n' * 3)

        driver.close()

        print(f"{idx} tests completed. {len(tests) - idx - 1} remaining")

    return len(tests)


if __name__ == "__main__":
    tests = get_test_case()
    starting_index = 0
    while True:
        test_idx = run_tests(tests, starting_index=starting_index)
        if test_idx == len(tests):
            break
        else:
            starting_index = test_idx

    arrange_files()



