{{- define "serverName" }}
{{- if eq .Values.deployType "PROD"}} "LCA Template"{{- else}} "LCA Test"{{- end}}
{{- end}}