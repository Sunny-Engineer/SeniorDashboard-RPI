import logging
import requests
import boto3
import os


def sd_register_device(register_device_params):
    #This routine registers a raspberry Pi with the global server
    # This routine returns a list of dashboards that need to be downloaded as new or updated dashboard files.
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    except Exception as e:
        # use print because we don't know if the logger is active!
        print("The routine Failed - {}".format(e))

    try:
        logger.info("Initiating - sd_register_device API Call")

        # Check to make sure that required fields are passed
        if "device_serial_number" not in register_device_params:
            logger.error("The required parameter device_serial_number is not included in parameter list.  - list = {}".format(register_device_params))
        if "device_type_id" not in register_device_params:
            logger.error("The required parameter device_type_id is not included in parameter list.  - list = {}".format(register_device_params))

        # call the API and return a dictionary.
        api_key_header = {'API_Key': 'test'}
        api_url = 'http://440documentmanagement-867640296.us-east-1.elb.amazonaws.com/api/RegisterDevice/'
        logger.info("About to call the sd_register_device API with the following parameters - {}".format(register_device_params))

        resp = requests.post(api_url, params=register_device_params, headers=api_key_header)

        # resp = requests.get('https://api.github.com/events')
        logger.info("completed request = {}".format(api_url))
        if resp.status_code != 200:
            # This means something went wrong, return a list of a single dictionary with results
            results = [{"status": "failed", "device_id": ""}, ]
            logger.info("The sd_register_device response = {}, resp.text = {}, reason = {}".format(resp, resp.text, resp.reason))
            raise NameError('POST /sdapi/GetDashboards/ {}'.format(resp.status_code))

        else:
            logger.info("Resp status code =  200! - Data returned = {}".format(resp.json()))
            # load results into json/dictionary
            results = resp.json()

        return results

    except Exception as e:
        logger.exception("The sd_register_device routine failed - {}".format(e))


def sd_download_dashboard_file(access_key, secret_key, bucket_name, key, local_path_file):
    # This call downloads the file returned from the dashboard record to a local directory.
    logging.getLogger()
    logger.setLevel(logging.INFO)

    client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, )
    logger.info ("Downloading the file_key = {} from bucket {}, to file location {} " .format(key, bucket_name, local_path_file))
    client.download_file(bucket_name, key, local_path_file)
    logger.info('Downloaded file with boto3 client - to {} ' .format(local_path_file))


def sd_getdashboards(get_dash_params):
    # This routine returns a list of dashboards that need to be downloaded as new or updated dashboard files.
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    except Exception as e:
        # use print because we don't know if the logger is active!
        print("The routine Failed - {}".format(e))


    try:
        logger.info ("Initiating - sd_getdashboards API Call")

        # Check to make sure that required fields are passed
        if "customer_id" not in get_dash_params:
            logger.error ("The required parameter customer_id is not included in parameter list.  - list = {}" .format(get_dash_params))

        # call the API and return a dictionary.
        api_key_header = {'API_Key': 'test'}
        api_url = 'http://440documentmanagement-867640296.us-east-1.elb.amazonaws.com/api/GetDashboards/'
        logger.info("About to call the GetDashboards API with the following parameters - {}".format(get_dash_params))

        resp = requests.get(api_url, params=get_dash_params, headers=api_key_header)

        # resp = requests.get('https://api.github.com/events')
        logger.info("completed request = {}".format(api_url))
        if resp.status_code != 200:
            # This means something went wrong, return a list of a single dictionary with results
            results = [{"status": "failed", "dashboard_id": ""},]
            logger.info("The GetDashboards response = {}, resp.text = {}, reason = {}".format(resp, resp.text, resp.reason))
            raise NameError('POST /sdapi/GetDashboards/ {}'.format(resp.status_code))

        else:
            logger.info("Resp status code =  200! - Data returned = {}" .format(resp.json()))
            # load results into json/dictionary
            results = resp.json()

        return results

    except Exception as e:
        logger.exception("The routine Failed - {}" .format(e))



if __name__ == '__main__':
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s.%(funcName)s - #%(lineno)-8s: [%(message)s]')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)  # only display info to the screen, debug to the file!
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        logger.info("Initializing the Test Routine For Senior Dashboard")

    except Exception as e:
        print ("The logger setup failed with error - {}" .format(e))

    # Get the AWS Credentials from local environmental variables
    try:
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")    # 
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region = os.environ.get("AWS_REGION")
        aws_perm_vault_bucket = os.environ.get("BR_PERM_VAULT")

    except Exception as e:
        logger.exception("The AWS environmental variables failed - {}" .format(e))

    try:
        logger.info("Initializing the register device test procedure.")

        register_device_params = {}

        # Required Parameters
        register_device_params["device_type_id"] = "12"
        register_device_params["device_mac_address"] = "12sd-3212k-34mdf-fd34"

        # Optional Parameters
        register_device_params["customer_id"] = "1"
        register_device_params["device_name"] = "1"
        register_device_params["device_night_end_time"] = "2018-12-18 20:00:00"
        register_device_params["device_night_start_time"] = "2018-12-18 20:00:00"
        register_device_params["device_serial_number"] = "123-23456-987734"
        register_device_params["device_status"] = "active"
        register_device_params["device_timezone"] = "eastern"
        register_device_params["device_uptdate_frequency"] = "3600"
        register_device_params["device_wireless_password"] = "GoOrange"
        register_device_params["device_wireless_ssid"] = "guestnetwork"
        register_device_params["user_email"] = "doug@dougbower.com"

        logger.info("About to register a device with the following parameters - {}" .format(register_device_params))

        register_response = sd_register_device(register_device_params)

        if isinstance(register_response, list):
            # This should return a list of one status dictionary.
            logger.info("A list...  Type of results =  {}".format(type(register_response)))
            for register_result in register_response:
                logger.info("Get Dashboard results = {}".format(register_result))
                if "device_id" in register_result:
                    device_id = register_result["device_id"]
                    logger.info(("device_id returned = {}".format(device_id)))
                else:
                    logger.info(("No device_id returned."))


    except Exception as e:
        logger.exception("The register device process test failed - {}" .format(e))


    try:
        # Get Dashboard Test Routine
        logger.info("-----------------------------------------------------------")
        logger.info("API - GetDashboards Test Routine")

        #provide the required customer_id and optional device_id.
        get_daqshboards_params = {}
        get_daqshboards_params["device_id"] = "1"
        get_daqshboards_params["customer_id"] = "12"

        get_dash_response = sd_getdashboards( get_daqshboards_params)

        # the response is a list of dictionaries.
        if isinstance(get_dash_response, list):
            # more than one result returned.  Use that last one returned.  We don't handle multiple destinations yet...
            logger.info("A list...  Type of results =  {}".format(type(get_dash_response)))
            for dash_result in get_dash_response:
                logger.info("Get Dashboard results = {}".format(dash_result))
                if "dashboard_name" in dash_result:
                    dashboard_name = dash_result["dashboard_name"]
                    logger.info(("Dashboard name returned = {}" .format(dashboard_name)))
                else:
                    logger.info(("No Dashboard name returned."))

                if "dashboard_file_bucketname" in dash_result:
                    dashboard_file_bucketname = dash_result["dashboard_file_bucketname"].strip('/')
                    logger.info(("dashboard_file_bucketname returned = {}".format(dashboard_file_bucketname)))
                else:
                    logger.info(("No dashboard_file_bucket returned."))

                if "dashboard_file_key" in dash_result:
                    dashboard_file_key = dash_result["dashboard_file_key"]
                    logger.info(("dashboard_file_key returned = {}".format(dashboard_file_key)))
                else:
                    logger.info(("No dashboard_file_key returned."))
        else:
            logger.info("The sd_getdiashboards API did not return a list of objects. - {}" .format(get_dash_response))

        # now download the file from s3 to a local file
        local_path_filename = "test.zip"
        file_download_results = sd_download_dashboard_file(aws_access_key_id, aws_secret_access_key, dashboard_file_bucketname, dashboard_file_key, local_path_filename )

        logger.info("The results of the file download = {}" .format(file_download_results))

    except Exception as error:
        logger.exception('The GetDashboards API routine failed: {} ' .format(error))
        logger.error('Response Code = {}'  .format(file_download_results.status_code))
        logger.error('Response Text = {}' .format(file_download_results.text))
        logger.error('Response Reason = {}'  .format(file_download_results.reason))
        logger.error('Parameters = {}' .format(get_daqshboards_params))

    finally:

        logger.info('Completed the GetDashboards API Test routine .')
        logger.info("-----------------------------------------------------------")