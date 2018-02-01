# Copyright 2014: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from rally.common import logging
from rally.common import utils
from rally.common import validation
from rally import consts
from rally.plugins.openstack import osclients
from rally.plugins.openstack.wrappers import network as network_wrapper
from rally.task import context


LOG = logging.getLogger(__name__)


# NOTE(andreykurilin): admin is used only by cleanup
@validation.add("required_platform", platform="openstack", admin=True,
                users=True)
@context.configure(name="network", platform="openstack", order=350)
class Network(context.Context):
    """Create networking resources.

    This creates networks for all tenants, and optionally creates
    another resources like subnets and routers.
    """

    CONFIG_SCHEMA = {
        "type": "object",
        "$schema": consts.JSON_SCHEMA,
        "properties": {
            "start_cidr": {
                "type": "string"
            },
            "networks_per_tenant": {
                "type": "integer",
                "minimum": 1
            },
            "subnets_per_network": {
                "type": "integer",
                "minimum": 1
            },
            "network_create_args": {
                "type": "object",
                "additionalProperties": True
            },
            "dns_nameservers": {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": True
            },
            "dualstack": {
                "type": "boolean",
            },
            "router": {
                "type": "object",
                "properties": {
                    "external": {
                        "type": "boolean"
                    },
                    "external_gateway_info": {
                        "description": "The external gateway information .",
                        "type": "object",
                        "properties": {
                            "network_id": {"type": "string"},
                            "enable_snat": {"type": "boolean"}
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    DEFAULT_CONFIG = {
        "start_cidr": "10.2.0.0/24",
        "networks_per_tenant": 1,
        "subnets_per_network": 1,
        "network_create_args": {},
        "dns_nameservers": None,
        "router": {"external": True},
        "dualstack": False
    }

    def setup(self):
        # NOTE(rkiran): Some clients are not thread-safe. Thus during
        #               multithreading/multiprocessing, it is likely the
        #               sockets are left open. This problem is eliminated by
        #               creating a connection in setup and cleanup separately.
        net_wrapper = network_wrapper.wrap(
            osclients.Clients(self.context["admin"]["credential"]),
            self, config=self.config)
        kwargs = {}
        if self.config["dns_nameservers"] is not None:
            kwargs["dns_nameservers"] = self.config["dns_nameservers"]
        for user, tenant_id in (utils.iterate_per_tenants(
                self.context.get("users", []))):
            self.context["tenants"][tenant_id]["networks"] = []
            for i in range(self.config["networks_per_tenant"]):
                # NOTE(amaretskiy): router_create_args and subnets_num take
                #                   effect for Neutron only.
                network_create_args = self.config["network_create_args"].copy()
                network = net_wrapper.create_network(
                    tenant_id,
                    dualstack=self.config["dualstack"],
                    subnets_num=self.config["subnets_per_network"],
                    network_create_args=network_create_args,
                    router_create_args=self.config["router"],
                    **kwargs)
                self.context["tenants"][tenant_id]["networks"].append(network)

    def cleanup(self):
        net_wrapper = network_wrapper.wrap(
            osclients.Clients(self.context["admin"]["credential"]),
            self, config=self.config)
        for tenant_id, tenant_ctx in self.context["tenants"].items():
            for network in tenant_ctx.get("networks", []):
                with logging.ExceptionLogger(
                        LOG,
                        "Failed to delete network for tenant %s" % tenant_id):
                    net_wrapper.delete_network(network)
