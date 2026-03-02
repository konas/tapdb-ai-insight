# -*- coding=utf-8 -*-
import argparse
import os

# BUILTIN_ENDPOINTS = {
#     "cn": "www.tapdb.com",
#     "sg": "console.ap-sg.tapdb.developer.taptap.com",
# }
#
# REGION_KEY_VARS = {
#     "cn": "TAPDB_MCP_KEY_CN",
#     "sg": "TAPDB_MCP_KEY_SG",
# }


class CliArgumentError(ValueError):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise CliArgumentError(message)


class CommonArgumentParser(ThrowingArgumentParser):
    """
    公共基础参数解析器：
    - 自动注入 -r/--region
    - parse_args 后自动补齐 args.mcp_key / args.endpoint
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        parsed = super().parse_args(args=args, namespace=namespace)
        enrich_args_with_region(parsed)
        return parsed


def enrich_args_with_region(args) -> None:
    # 优先检查TAPDB_MCP_KEY_CN，其次检查TAPDB_MCP_KEY_SG
    mcp_key = os.environ.get("TAPDB_MCP_KEY_CN")
    if mcp_key is not None:
        args.mcp_key = mcp_key
        args.endpoint = "www.tapdb.com"
    else:
        mcp_key = os.environ.get("TAPDB_MCP_KEY_SG")
        if mcp_key is not None:
            args.mcp_key = mcp_key
            args.endpoint = "console.tapdb.developer.taptap.com"
        else:
            raise CliArgumentError(f"环境变量未设置TAPDB_MCP_KEY_CN或者TAPDB_MCP_KEY_SG")




