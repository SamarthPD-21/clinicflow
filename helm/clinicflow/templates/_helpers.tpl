{{- define "clinicflow.name" -}}clinicflow{{- end }}

{{- define "clinicflow.labels" -}}
app.kubernetes.io/part-of: clinicflow
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "clinicflow.dbSecret" -}}
{{- default (printf "%s-postgres" .Release.Name) .Values.postgres.existingSecret -}}
{{- end }}

{{- define "clinicflow.pullSecrets" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets:
{{- toYaml . | nindent 2 }}
{{- end }}
{{- end }}
