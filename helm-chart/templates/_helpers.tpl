{{- define "flaskapp.name" -}}
{{- printf "%s-%s" .Release.Name "flaskapp" | trunc 63 | trimSuffix "-" -}}
{{- end -}}