# networklytics-mcp

[NetworkLytics](https://networklytics.com) MCP (Model Context Protocol) server.

Claude Desktop, Cursor 등 MCP 지원 AI 도구에서 YouTube 댓글 네트워크 분석 결과를 직접 조회할 수 있습니다.

## 설치

```bash
pip install networklytics-mcp
```

## Claude Desktop 설정

`~/.claude/claude_desktop_config.json` 또는 `%APPDATA%\Claude\claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "networklytics": {
      "command": "networklytics-mcp",
      "env": {
        "NETWORKLYTICS_API_URL": "https://networklytics.com",
        "NETWORKLYTICS_API_KEY": "nly_your_api_key_here"
      }
    }
  }
}
```

API 키는 NetworkLytics 계정 설정 페이지에서 발급받을 수 있습니다.

## 사용 예시

Claude에서 다음과 같이 요청할 수 있습니다:

- "이 공유 링크 분석 결과를 보여줘: https://networklytics.com/shared/abc-123-..."
- "분석 결과에서 핵심 인플루언서 3명을 찾아줘"
- "이 YouTube 채널 댓글 커뮤니티의 감성 트렌드는 어때?"

## 제공 도구 (Tools)

| Tool | 설명 | 인증 |
|------|------|------|
| `get_shared_analysis` | 공유 링크 토큰으로 분석 결과 조회 | 불필요 |
| `get_analysis_by_id` | 분석 ID로 결과 조회 | API 키 필요 |
| `get_api_info` | API 정보 및 엔드포인트 목록 | 불필요 |

## 반환 데이터 구조

```json
{
  "video": { "title": "...", "channel": "...", "view_count": 123456 },
  "network": {
    "total_nodes": 1500,
    "total_edges": 3200,
    "density": 0.003,
    "community_count": 7
  },
  "sentiment": {
    "positive_ratio": 0.62,
    "negative_ratio": 0.15,
    "overall": "positive"
  },
  "top_influencers": [
    { "author": "username", "degree_centrality": 0.12, "comment_count": 45 }
  ],
  "topic_keywords": ["키워드1", "키워드2"],
  "ai_insights": { ... }
}
```
