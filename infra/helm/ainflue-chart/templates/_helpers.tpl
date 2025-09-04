{{/*
Expand the name of the chart.
*/}}
{{- define "ainflue.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ainflue.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ainflue.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ainflue.labels" -}}
helm.sh/chart: {{ include "ainflue.chart" . }}
{{ include "ainflue.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
environment: {{ .Values.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ainflue.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ainflue.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ainflue.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ainflue.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database host
*/}}
{{- define "ainflue.databaseHost" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "ainflue.fullname" .) }}
{{- else }}
{{- .Values.config.database.host }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "ainflue.redisHost" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "ainflue.fullname" .) }}
{{- else }}
{{- .Values.config.redis.host }}
{{- end }}
{{- end }}

{{/*
Common environment variables
*/}}
{{- define "ainflue.commonEnv" -}}
- name: DATABASE_HOST
  value: {{ include "ainflue.databaseHost" . | quote }}
- name: DATABASE_PORT
  value: {{ .Values.config.database.port | quote }}
- name: DATABASE_NAME
  value: {{ .Values.config.database.name | quote }}
- name: DATABASE_USERNAME
  value: {{ .Values.config.database.username | quote }}
- name: REDIS_HOST
  value: {{ include "ainflue.redisHost" . | quote }}
- name: REDIS_PORT
  value: {{ .Values.config.redis.port | quote }}
- name: ENVIRONMENT
  value: {{ .Values.config.app.environment | quote }}
- name: LOG_LEVEL
  value: {{ .Values.config.app.logLevel | quote }}
- name: API_VERSION
  value: {{ .Values.config.app.apiVersion | quote }}
- name: MAX_WORKERS
  value: {{ .Values.config.app.maxWorkers | quote }}
- name: WORKER_TIMEOUT
  value: {{ .Values.config.app.workerTimeout | quote }}
- name: CORS_ORIGINS
  value: {{ .Values.config.app.corsOrigins | quote }}
- name: UPLOAD_MAX_SIZE
  value: {{ .Values.config.app.uploadMaxSize | quote }}
- name: SESSION_TIMEOUT
  value: {{ .Values.config.app.sessionTimeout | quote }}
- name: RATE_LIMIT_REQUESTS
  value: {{ .Values.config.app.rateLimitRequests | quote }}
- name: RATE_LIMIT_WINDOW
  value: {{ .Values.config.app.rateLimitWindow | quote }}
{{- end }}

{{/*
Common secret environment variables
*/}}
{{- define "ainflue.secretEnv" -}}
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: database-password
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: secret-key
- name: JWT_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: jwt-secret
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: openai-api-key
- name: ELEVENLABS_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: elevenlabs-api-key
- name: STRIPE_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: stripe-secret-key
- name: STRIPE_PUBLISHABLE_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: stripe-publishable-key
- name: SHOPIFY_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: shopify-api-key
- name: MIDJOURNEY_API_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ include "ainflue.fullname" . }}-secrets
      key: midjourney-api-token
{{- end }}

{{/*
Image pull policy
*/}}
{{- define "ainflue.imagePullPolicy" -}}
{{- .Values.image.pullPolicy | default "IfNotPresent" }}
{{- end }}

{{/*
Resource definitions
*/}}
{{- define "ainflue.resources" -}}
{{- if . }}
resources:
  {{- if .requests }}
  requests:
    {{- if .requests.memory }}
    memory: {{ .requests.memory }}
    {{- end }}
    {{- if .requests.cpu }}
    cpu: {{ .requests.cpu }}
    {{- end }}
    {{- if index .requests "nvidia.com/gpu" }}
    nvidia.com/gpu: {{ index .requests "nvidia.com/gpu" }}
    {{- end }}
  {{- end }}
  {{- if .limits }}
  limits:
    {{- if .limits.memory }}
    memory: {{ .limits.memory }}
    {{- end }}
    {{- if .limits.cpu }}
    cpu: {{ .limits.cpu }}
    {{- end }}
    {{- if index .limits "nvidia.com/gpu" }}
    nvidia.com/gpu: {{ index .limits "nvidia.com/gpu" }}
    {{- end }}
  {{- end }}
{{- end }}
{{- end }}