{{- define "nginx-litellm-proxy.name" -}}
nginx-litellm-proxy
{{- end }}

{{- define "nginx-litellm-proxy.fullname" -}}
{{ include "nginx-litellm-proxy.name" . }}
{{- end }}
