"""
NetworkLytics MCP Server

Claude Desktop / Cursor 등에서 YouTube 댓글 네트워크 분석 결과를 직접 조회할 수 있게 해주는
MCP (Model Context Protocol) 서버.

설치:
    pip install networklytics-mcp

Claude Desktop 설정 (~/.claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "networklytics": {
          "command": "networklytics-mcp",
          "env": {
            "NETWORKLYTICS_API_URL": "https://networklytics.net",
            "NETWORKLYTICS_API_KEY": "nly_your_api_key_here"
          }
        }
      }
    }
"""
import json
import os
import sys
from typing import Any

import httpx

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print(
        "ERROR: 'mcp' package not found. Install with: pip install mcp",
        file=sys.stderr,
    )
    sys.exit(1)


API_URL = os.environ.get('NETWORKLYTICS_API_URL', 'https://networklytics.net').rstrip('/')
API_KEY = os.environ.get('NETWORKLYTICS_API_KEY', '')

server = Server('networklytics')


def _headers() -> dict:
    if API_KEY:
        return {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}
    return {'Accept': 'application/json'}


def _get(path: str, params: dict | None = None) -> dict:
    url = f'{API_URL}/api/v1{path}'
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, headers=_headers(), params=params or {})
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name='get_shared_analysis',
            description=(
                'Retrieve a YouTube comment network analysis result from a public NetworkLytics share link. '
                'Returns network statistics (nodes, edges, density, communities), '
                'top influencers with centrality scores, sentiment analysis, '
                'topic keywords, and AI-generated insights. '
                'Use this when a user shares a NetworkLytics share URL or token.'
            ),
            inputSchema={
                'type': 'object',
                'properties': {
                    'token': {
                        'type': 'string',
                        'description': (
                            'Share link token (UUID) or full NetworkLytics share URL. '
                            'Example: "a1b2c3d4-..." or "https://networklytics.com/shared/a1b2c3d4-..."'
                        ),
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Password for password-protected share links (optional)',
                    },
                },
                'required': ['token'],
            },
        ),
        types.Tool(
            name='get_analysis_by_id',
            description=(
                'Retrieve a YouTube comment network analysis by its ID. '
                'Requires API key authentication (set NETWORKLYTICS_API_KEY environment variable). '
                'Returns the same structured data as get_shared_analysis.'
            ),
            inputSchema={
                'type': 'object',
                'properties': {
                    'analysis_id': {
                        'type': 'integer',
                        'description': 'The numeric analysis ID from NetworkLytics',
                    },
                },
                'required': ['analysis_id'],
            },
        ),
        types.Tool(
            name='get_api_info',
            description='Get NetworkLytics API information and available endpoints.',
            inputSchema={'type': 'object', 'properties': {}, 'required': []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == 'get_shared_analysis':
            token = arguments['token']
            # URL에서 토큰 추출
            if 'shared/' in token:
                token = token.split('shared/')[-1].strip('/')
            params = {}
            if 'password' in arguments:
                params['password'] = arguments['password']
            data = _get(f'/shared/{token}/', params)
            return [types.TextContent(type='text', text=json.dumps(data, ensure_ascii=False, indent=2))]

        elif name == 'get_analysis_by_id':
            analysis_id = arguments['analysis_id']
            data = _get(f'/analyses/{analysis_id}/')
            return [types.TextContent(type='text', text=json.dumps(data, ensure_ascii=False, indent=2))]

        elif name == 'get_api_info':
            data = _get('/')
            return [types.TextContent(type='text', text=json.dumps(data, ensure_ascii=False, indent=2))]

        else:
            return [types.TextContent(type='text', text=f'Unknown tool: {name}')]

    except httpx.HTTPStatusError as e:
        error_body = {}
        try:
            error_body = e.response.json()
        except Exception:
            error_body = {'raw': e.response.text}
        return [types.TextContent(
            type='text',
            text=json.dumps({'error': str(e), 'detail': error_body}, ensure_ascii=False),
        )]
    except Exception as e:
        return [types.TextContent(type='text', text=json.dumps({'error': str(e)}, ensure_ascii=False))]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    import asyncio
    asyncio.run(_run())


if __name__ == '__main__':
    main()
