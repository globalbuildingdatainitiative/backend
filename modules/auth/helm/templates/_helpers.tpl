{{/*
Create env list.
*/}}
{{- define "supertokens.env" }}
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{.Values.db.secret.name }}
      key: password
- name: DATABASE_USERNAME
  valueFrom:
    secretKeyRef:
      name: {{.Values.db.secret.name }}
      key: username
- name: DATABASE_HOST
  valueFrom:
    configMapKeyRef:
      name: {{ .Values.db.configmap }}
      key: POSTGRES_HOST
- name: DATABASE_PORT
  valueFrom:
    configMapKeyRef:
      name: {{ .Values.db.configmap }}
      key: POSTGRES_PORT
- name: DATABASE_NAME
  valueFrom:
    configMapKeyRef:
      name: {{ .Values.db.configmap }}
      key: POSTGRES_DB
-  { name: POSTGRESQL_CONNECTION_URI, value: "{{ printf "postgresql://$(DATABASE_USERNAME):$(DATABASE_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/$(DATABASE_NAME)" }}"}
{{- end -}}