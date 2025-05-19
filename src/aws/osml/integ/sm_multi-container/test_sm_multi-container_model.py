#  Copyright 2025 Amazon.com, Inc. or its affiliates.

import logging

from aws.osml.utils import (
    OSMLConfig,
    count_features,
    count_region_request_items,
    ddb_client,
    kinesis_client,
    run_model_on_image,
    s3_client,
    sqs_client,
    validate_expected_region_request_items,
    validate_features_match,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_model_runner_multi_container_center_point_model() -> None:
    """
    Run the test using the SageMaker multi container endpoint (centerpoint container) and validate the
    number of features and region requests

    :return: None
    """

    expected_results_file = "./src/data/centerpoint.small.tif.geojson"
    # launch our image request and validate it completes
    image_id, job_id, image_processing_request, shard_iter = run_model_on_image(
        sqs_client(),
        OSMLConfig.SM_MULTI_CONTAINER_ENDPOINT,
        "SM_ENDPOINT",
        kinesis_client(),
        target_container="centerpoint-container",
    )

    # count the features created in the table for this image
    count_features(image_id=image_id, ddb_client=ddb_client())

    # verify the results we created in the appropriate sinks
    validate_features_match(
        image_processing_request=image_processing_request,
        job_id=job_id,
        shard_iter=shard_iter,
        s3_client=s3_client(),
        kinesis_client=kinesis_client(),
        result_file=expected_results_file,
    )

    # validate the number of region requests that were created in the process and check if they are succeeded
    region_request_count = count_region_request_items(image_id=image_id, ddb_client=ddb_client())
    validate_expected_region_request_items(region_request_count)


def test_model_runner_multi_container_aircraft_model() -> None:
    """
    Run the test using the SageMaker multi container endpoint (aircraft container) and validate the
    number of features and region requests

    :return: None
    """

    expected_results_file = "./src/data/aircraft.small.tif.geojson"
    # launch our image request and validate it completes
    image_id, job_id, image_processing_request, shard_iter = run_model_on_image(
        sqs_client(),
        OSMLConfig.SM_MULTI_CONTAINER_ENDPOINT,
        "SM_ENDPOINT",
        kinesis_client(),
        target_container="aircraft-container",
    )

    # count the features created in the table for this image
    count_features(image_id=image_id, ddb_client=ddb_client())

    # verify the results we created in the appropriate sinks
    validate_features_match(
        image_processing_request=image_processing_request,
        job_id=job_id,
        shard_iter=shard_iter,
        s3_client=s3_client(),
        kinesis_client=kinesis_client(),
        result_file=expected_results_file,
    )

    # validate the number of region requests that were created in the process and check if they are succeeded
    region_request_count = count_region_request_items(image_id=image_id, ddb_client=ddb_client())
    validate_expected_region_request_items(region_request_count)
