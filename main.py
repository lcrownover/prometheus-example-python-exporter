from time import sleep

import requests
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client.registry import Collector

INTERVAL_SECONDS = 5


# This is just an example of querying a REST endpoint and returning the JSON response
# converted to a Python dictionary
#
# Example response dict:
# {'watts': 414.755561102181, 'active_nodes': 97, 'flesh_recycler_overdrive_state': 0}
#
def get_the_data() -> dict[str, int | float]:
    resp = requests.get(
        "https://oveeblebtyqqgalxzbhwhp4z4i0yhjek.lambda-url.us-west-2.on.aws/"
    )
    return resp.json()


class CustomCollector(Collector):
    def collect(self):
        # Go get data from the API
        data = get_the_data()

        #######################################################################
        # METRIC: Electrical Wattage Used for Recycling Flesh
        #######################################################################
        # Create metrics
        # I like to use long metric names to help me categorize metrics
        gauge_watts = GaugeMetricFamily(
            name="myproject_mycategory_myservice_watts",
            documentation="Electrical Wattage Used for Recycling Flesh",
        )
        # The best way to describe the labels are things that you might want to
        # filter for.
        gauge_watts.add_metric(
            value=data["watts"],
            labels=[
                "https://oveeblebtyqqgalxzbhwhp4z4i0yhjek.lambda-url.us-west-2.on.aws/",
                "aws",
            ],
        )
        # For example, I can scrape the SAME metric multiple times as
        # long as the labels are different, then I can have multiple lines on my
        # graph for the same metric name. Using the labels, I can filter by, for
        # example, where the metric is queried from (say I have to different APIs)
        # I'm hitting.
        # gauge_watts.add_metric(
        #     value=data["watts"],    # same value
        #     labels=[                # different labels
        #         "https://some-other-aws-url/",
        #         "aws",
        #     ],
        # )

        # Yield that metric, which lets the function keep executing
        yield gauge_watts
        #######################################################################

        #######################################################################
        # METRIC: Number of Active Flesh Recycling Nodes
        #######################################################################
        gauge_active_nodes = GaugeMetricFamily(
            name="myproject_mycategory_myservice_active_nodes",
            documentation="Number of Active Flesh Recycling Nodes",
        )
        gauge_active_nodes.add_metric(
            value=data["active_nodes"],
            labels=[
                "https://oveeblebtyqqgalxzbhwhp4z4i0yhjek.lambda-url.us-west-2.on.aws/",
                "aws",
            ],
        )
        yield gauge_active_nodes
        #######################################################################

        #######################################################################
        # METRIC: Flesh Recycler Overdrive ON(1) or OFF(0)
        #######################################################################
        gauge_fr_od_state = GaugeMetricFamily(
            name="myproject_mycategory_myservice_flesh_recycler_overdrive_state",
            documentation="Flesh Recycler Overdrive ON(1) or OFF(0)",
        )
        gauge_fr_od_state.add_metric(
            value=data["flesh_recycler_overdrive_state"],
            labels=[
                "https://oveeblebtyqqgalxzbhwhp4z4i0yhjek.lambda-url.us-west-2.on.aws/",
                "aws",
            ],
        )
        yield gauge_fr_od_state
        #######################################################################


# The main function to run
if __name__ == "__main__":
    # Register the collector
    REGISTRY.register(CustomCollector())

    # Show a server startup message
    LISTEN_PORT = 8000
    print(f"Starting Prometheus Example Python Collector on 0.0.0.0{LISTEN_PORT}")

    # Start up the server to expose the metrics.
    start_http_server(LISTEN_PORT)

    # Keep the exporter running
    while True:
        try:
            # 10 seconds is arbitrary, metrics will be gathered whenever
            # 0.0.0.0:8000/metrics is hit. We just want to sleep some number so
            # the CPU doesn't sit pegged at 100%.
            sleep(10)
        except KeyboardInterrupt:
            # This just gracefully handles CTRL+C without a nasty error
            exit(0)
