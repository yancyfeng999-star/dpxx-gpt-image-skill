# RootFlowAI GPT API Notes

Base URL:

```text
https://api.rootflowai.com/v1
```

Authentication:

```text
Authorization: Bearer <ROOTFLOWAI_GPT_API_KEY>
```

Supported GPT image models:

- `gpt-image-2-count`
- `gpt-image-2-hd-count`
- `gpt-image-2-4k-count`

Generation endpoint:

```text
POST /images/generations
```

Edit endpoint:

```text
POST /images/edits
```

The request may include `quality` for GPT models. The default is `high`.
