from time import sleep

import requests
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client.registry import Collector

#
# Dependencies
#
# You'll need to install the following packages using `pip`:
#   requests
#   types-requests
#   prometheus-client
#
# Like so: `pip install requests types-requests prometheus-client`
#


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


#
# Background information on why we need a CustomCollector
#
# This CustomCollector isn't strictly necessary, but is good practice.
# The default python prometheus docs collect on an interval and returns the newest
# data whenever the /metrics endpoint is queried. This is inefficient, and we'd
# rather wait to collect the metrics until the /metrics endpoint is queried.
# To accomplish this, we need a little more boilerplate, seen below.
class CustomCollector(Collector):
    # This method is called whenever /metrics is queried.
    def collect(self):
        # Go get data from the API and store it in the `data` dict.
        data = get_the_data()

        #
        # Creating metrics
        # I like to use long metric names to help me categorize metrics
        # For the documentation field, think of this like what you'd use
        # as the title of the graph in Grafana.
        #

        #######################################################################
        # METRIC: Electrical Wattage Used for Recycling Flesh
        #######################################################################
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
        # that I'm hitting.
        #
        # gauge_watts.add_metric(
        #     value=data["watts"],    # same value
        #     labels=[                # different labels
        #         "https://some-other-aws-url/",
        #         "aws",
        #     ],
        # )
        #

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
    # Register our CustomCollector
    REGISTRY.register(CustomCollector())

    # Show a server startup message so you have some logging
    LISTEN_PORT = 8000
    print(f"Starting Prometheus Example Python Collector on 0.0.0.0{LISTEN_PORT}")

    # Start up the server which exposes the metrics at 0.0.0.0:LISTEN_PORT/metrics
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
