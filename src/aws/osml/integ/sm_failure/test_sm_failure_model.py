#  Copyright 2023 Amazon.com, Inc. or its affiliates.

import logging

from aws.osml.utils import (
    OSMLConfig,
    analyze_failure_model_results,
    count_features,
    count_region_request_items,
    ddb_client,
    kinesis_client,
    run_failure_model_on_image,
    s3_client,
    sqs_client,
    validate_expected_region_request_items,
    validate_features_match,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_model_runner_failure_model() -> None:
    """
    Run the test using the Failure Model and validate the number of successful tiles and handling of various failure types

    :return: None
    """

    # launch our image request and validate it completes
    image_id, job_id, image_processing_request, shard_iter = run_failure_model_on_image(
        sqs_client(), OSMLConfig.SM_FAILURE_MODEL, "SM_ENDPOINT", kinesis_client()
    )
    failure_results = analyze_failure_model_results(image_id=image_id, ddb_client=ddb_client())

    # Validate based on results
    if failure_results["failed_tiles"] == 0:
        # No failures - normal validation
        count_features(image_id=image_id, ddb_client=ddb_client())

        # verify the results we created in the appropriate sinks
        validate_features_match(
            image_processing_request=image_processing_request,
            job_id=job_id,
            shard_iter=shard_iter,
            s3_client=s3_client(),
            kinesis_client=kinesis_client(),
        )

        # validate the number of region requests that were created in the process and check if they are succeeded
        region_request_count = count_region_request_items(image_id=image_id, ddb_client=ddb_client())
        validate_expected_region_request_items(region_request_count)
    else:
        # Has failures - validate counts
        if "failure_model_checker" in image_id:
            assert failure_results["total_tiles"] == 16
            assert (
                failure_results["failed_tiles"] == 4 and failure_results["failed_tiles"] < failure_results["total_tiles"]
            )  # failed tiles should not be all of them
            assert failure_results["successful_tiles"] == 12
            assert failure_results["region_status"] == "PARTIAL"  # result should be a PARTIAL type
            logging.info("Checkerboard failures passed!")
        logging.info(f"Results: {failure_results}")
