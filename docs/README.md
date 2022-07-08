# BoostUp QA Solution

## Setup

### Pre-requisites
- Install Git: https://github.com/git-guides/install-git
- Install Python 3.8: https://www.python.org/downloads/release/python-380/
  - (the testing solution is not proven yet to work with Python 3.9)
- Install pipenv: https://pypi.org/project/pipenv
- Install the testing solution:
  - Open a command line in a folder where you want to store the testing soltion
  - Execute: ```git clone https://github.com/Vocalo/automation-tests```
    - (Confirm you can login to github and see the 'automation-tests' repository)

### The tests need the following environment variables to be set:
For environment variables, duplicate .env-sample and rename it to .env. Then edit the .env file with your own values.

OR

Set the environment variables in the command line:
- APP_URL
  - Windows: ```set APP_URL=https://app.boostup.ai/```
  - Linux: ```export APP_URL=https://app.boostup.ai/"```
- SSO_ADMIN_EMAIL
  - Windows: ```set SSO_ADMIN_EMAIL=<your_boostup_email>```
  - Linux: ```export SSO_ADMIN_EMAIL='<your_boostup_email>'```
- SSO_ADMIN_PASSWORD
  - Windows: ```set SSO_ADMIN_PASSWORD=<your_sso_password>```
  - Linux: ```export SSO_ADMIN_PASSWORD=<your_sso_password>```
- SSO_ADMIN_TFA
  - Windows: ```set SSO_ADMIN_TFA=<your_secret_key>```
  - Linux: ```export SSO_ADMIN_TFA=<your_secret_key>```
    The testing solution automatically generates the OTP code based on the secret key

### Install testing solution dependencies
From root project folder execute the following command: ```pipenv install```

### To execute tests locally:
Execute the following command, by replacing \<TAG\> by any scenario tags you would like to execute:
```
pipenv run behavex -t BOOSTUP -t <TAG> -D browser=chrome
```

### Testing solution documentation
As the testing solution consists of a wrapper (called BehaveX) on top of Python Behave, please take a look at the Behave documentation:
https://behave.readthedocs.io/en/stable/

### APPIUM
Install Node LTS
```
https://nodejs.org/en/download/
```

Install APPIUM
```
npm install -g appium@1.18.3   # Warning: Needs this specific version in order to execute the test without errors
```
Set Environment Variables

- BROWSER_STACK_USER
  - Windows: ```set BROWSER_STACK_USER=<your_secret_key>```
  - Linux: ```export BROWSER_STACK_USER=<your_secret_key>```
- BROWSER_STACK_KEY
  - Windows: ```set BROWSER_STACK_KEY=<your_secret_key>```
  - Linux: ```export BROWSER_STACK_KEY=<your_secret_key>```

To run on your AVD locally run the following command
```
pipenv run behavex -t ANDROID -D local
```

To run on BrowserStack execute the following command
```
pipenv run behavex -t ANDROID -D remote
```

### Compare data across releases
In order to compare data across releases, we are providing a Postman collection that contains the plans that retrieve all data from RollUps/Opportunities pages.

The plans to launch are available in the following Postman collection:

```CircleCI - QA Regressions --> Data Compare```

As an example, if you need to compare Rollups metrics and table data between PREPROD and PREPROD2 environments, you should launch in parallel the following plans:

* ROLLUPS - PREPROD
* ROLLUPS - PREPROD2

Once executions are completed, you need to download the following artifact from circleci:

```output/data_compare_files/data_compare_files.zip```

Then, you need to unzip the artifact from both executions in separate folders, and run the following command from the root folder of the testing solution:

```pipenv run python .\utils\data_compare\compare_csv_data.py <absolute_path_folder_1> <absolute_path_folder_2>```

Once executed the *data_compare_outputs.csv* file will be generated with the data mismatches

### Capture and Compare Endpoint Responses (to enable comparing)
#### Capture Endpoint Responses
**Note**: This step is already being performed from CircleCI (see <a href="ucapture-responses-postman">here</a>). So, you can skip this section if you are not planning to locally trigger the execution that log all endpoint responses.

To capture endpoint responses, you need to set the following environment variable:
- Windows: ```set CAPTURE_ENDPOINT_RESPONSES=true```
- Linux: ```export CAPTURE_ENDPOINT_RESPONSES=true```

Run the test scenarios that should be part of the locust test suite
```
pipenv run behavex -t <TAGS> -D browser=chrome
```

Verify the following file is generated in output folder:
```
<output_folder>/endpoint_responses.zip
```

#### Compare Endpoint Responses
To compare endpoint responses, you need to use following script that is provided as part of the testing solution:
```
pipenv run python .\utils\backend_response_comparer\compare_responses.py --help
```

The following is the command for comparing endpoint schemas from a couple of executions:
```
pipenv run python .\utils\backend_response_comparer\compare_responses.py <folder_a> <folder_b>
```
Sample:
```
pipenv run python .\utils\backend_response_comparer\compare_responses.py C:\Temp\output_1 C:\Temp\output_2
```

(it is important to mention that the .zip files should be extracted to the folders specified as arguments)

<!----><a name="capture-responses-postman"></a>
#### Launching an execution from Postman:
The following is the Postman collection request that allows you to perform the execution that collect endpoint responses:
```
CircleCI - QA Regressions --> QA Regression - COMPARE BACKENDS
```

The request body looks like this:
```
{
    "branch": "master",
    "parameters": {
        "test_execution_name": "CAPTURE ENDPOINT RESPONSES",
        "env_name": "production",
        "app_url": "https://app.boostup.ai/",
        "capture_endpoint_responses": "true",
        "compare_endpoint_responses": "true"
    }
}
```
Once executed, the endpoint response files can be found in the CircleCI artifacts, in the following .zip file:
```
output/endpoint_responses_1.zip
```


### LOCUST (Performance Testing)
To generate the locust test file, you need to set the following environment variable:
- Windows: ```set CREATE_LOCUST_TESTS=true```
- Linux: ```export CREATE_LOCUST_TESTS=true```


Run the test scenarios that should be part of the locust test suite
```
pipenv run behavex -t <TAGS> -D browser=chrome
```

Verify the Locust test files were created in the following path:
```
.\output\locust\locust_utils.py
.\output\locust\locust_file.py
```

Run the locust by executing the following command:
```
pipenv run locust -f .\output\locust_file.py --host https://staging.boostup.ai/
```

Once locust is running, open the Locust web page to launch the tests:
```
http://localhost:8089/
```
