# 🚀 وحدة الخدمات - هندسة الخدمات المصغرة للمؤسسات

## نظرة عامة

تُنفذ وحدة الخدمات في منصة Ainflue هندسة خدمات مصغرة عالمية المستوى للمؤسسات مع فصل ثلاثي الطبقات لتحقيق أفضل قابلية للتوسع والأمان والأداء.

## 🏗️ الهندسة ثلاثية الطبقات

### 🔧 الطبقة الأولى: الخدمات الأساسية (الأساس)
خدمات البنية التحتية الأساسية للاكتشاف والصحة والأحداث والتكوين.

- **ServiceRegistry**: اكتشاف الخدمات مع موازنة التحميل الذكية
- **HealthMonitor**: مراقبة الصحة مع قواطع الدوائر والاستعادة التلقائية
- **EventBus**: هندسة مدفوعة بالأحداث مع أنماط النشر/الاشتراك
- **ConfigManager**: إدارة التكوين مع إعادة التحميل المباشر وإدارة الأسرار
- **LifecycleManager**: إدارة دورة حياة الخدمة مع تتبع التبعيات
- **MetricsCollector**: تكامل Prometheus مع كشف الشذوذ والتنبيهات

### ⚙️ الطبقة الثانية: خدمات المعالجة (منطق العمل)
خدمات معالجة الأعمال للمحتوى والذكاء الاصطناعي والوسائط والتوصيات.

- **ContentProcessor**: معالجة المحتوى متعدد التنسيقات مع التحقق المتقدم
- **AIOrchestrator**: تنسيق الذكاء الاصطناعي متعدد المزودين مع التوجيه الذكي
- **MediaPipeline**: خط أنابيب معالجة الوسائط مع البث المباشر
- **RecommendationEngine**: محرك التوصيات مع تحليلات التعلم الآلي
- **ValidationService**: خدمة التحقق مع القواعد الشاملة
- **TransformationEngine**: محرك تحويل المحتوى

### 🎯 الطبقة الثالثة: خدمات التنسيق (التنسيق)
خدمات التنسيق لسير العمل وذكاء الأعمال والأتمتة.

## 🔒 أمان المؤسسات

- **المصادقة من خدمة إلى خدمة**: mTLS + JWT
- **التحقق من المدخلات**: تطهير صارم عبر جميع الخدمات
- **إدارة الأسرار**: تكامل Vault مع التشفير
- **تسجيل التدقيق**: إمكانية تتبع كاملة لجميع استدعاءات الخدمة
- **تقييد المعدل**: حماية DDoS مع العتبات الذكية

## ⚡ أداء محسن للغاية

- **وقت استجابة API**: < 100 مللي ثانية (P95)
- **استنتاج الذكاء الاصطناعي**: < 500 مللي ثانية (P95)
- **خط أنابيب المعالجة**: تحسين التوازي
- **ذاكرة التخزين المؤقت الذكية**: متعددة المستويات (L1/L2/L3)
- **تجميع الاتصالات**: تحسين الموارد
- **التوسع التلقائي**: توسع أفقي تفاعلي

## 🎵 معالجة الصوت الاحترافية

- **التنسيقات المدعومة**: MP3, WAV, FLAC, AAC, OGG, M4A, OPUS
- **البث المباشر**: بث صوتي مستمر
- **تحسين الجودة**: خوارزميات التعلم الآلي لتحسين الصوت
- **توحيد الصوت**: معادلة تلقائية للمستويات
- **إزالة الصمت**: تحسين ذكي للمحتوى

## 📊 قابلية المراقبة الكاملة

- **مقاييس Prometheus**: قياسية + مقاييس مخصصة
- **لوحات معلومات Grafana**: في الوقت الفعلي + تاريخية
- **التسجيل المنظم**: JSON + معرفات الارتباط
- **التتبع الموزع**: تتبع تدفق الطلبات
- **تتبع الأخطاء**: تكامل Sentry
- **مقاييس الأعمال**: تتبع مؤشرات الأداء الرئيسية

## 🚀 البداية السريعة

```bash
# تثبيت التبعيات
pip install -r requirements.txt

# بدء Redis
redis-server

# بدء الخدمات
python -m services.core.service_registry
python -m services.processing.ai_orchestrator
python -m services.processing.media_pipeline
```

## 📝 التكوين

```yaml
# services/config/services.yaml
service_registry:
  redis_url: "redis://localhost:6379"
  health_check_interval: 30

ai_orchestrator:
  max_concurrent_tasks: 100
  routing_strategy: "cost_performance"

media_pipeline:
  max_concurrent_jobs: 10
  enable_quality_enhancement: true
```

## 🔧 الاستخدام

### تسجيل الخدمة

```python
from services import ServiceRegistry, ServiceInstance, ServiceType

registry = ServiceRegistry()
await registry.initialize()

service = ServiceInstance(
    service_id="my-service",
    service_name="My Service",
    service_type=ServiceType.PROCESSING,
    host="localhost",
    port=8080,
    health_endpoint="/health"
)

await registry.register_service(service)
```

### معالجة الذكاء الاصطناعي

```python
from services import AIOrchestrator, AITask, AITaskType

orchestrator = AIOrchestrator()
await orchestrator.initialize()

task = AITask(
    task_id="generate-content",
    task_type=AITaskType.TEXT_GENERATION,
    prompt="إنشاء ملخص لهذا المقال"
)

task_id = await orchestrator.submit_task(task)
result = await orchestrator.get_task_status(task_id)
```

### خط أنابيب الوسائط

```python
from services import MediaPipeline, MediaType

pipeline = MediaPipeline()
await pipeline.initialize()

# رفع ملف صوتي
with open("audio.mp3", "rb") as f:
    data = f.read()

asset_id = await pipeline.upload_media(
    file_data=data,
    filename="audio.mp3",
    media_type=MediaType.AUDIO
)

# تتبع المعالجة
status = await pipeline.get_asset_status(asset_id)
```

## 🎯 المقاييس والمراقبة

توفر الوحدة مقاييس شاملة لجميع الخدمات:

- **مقاييس الأداء**: وقت الاستجابة، المعدل، معدل الخطأ
- **مقاييس الموارد**: المعالج، الذاكرة، الشبكة، القرص
- **مقاييس الأعمال**: عدد المستخدمين، الطلبات المعالجة، التكاليف
- **مقاييس الجودة**: نتيجة الجودة، كشف الشذوذ

## 🔄 قواطع الدوائر

حماية تلقائية ضد الأعطال المتتالية:

```python
from services import HealthMonitor, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout_seconds=60,
    success_threshold=3
)
```

## 📈 التوسع التلقائي

توسع تلقائي بناءً على المقاييس:

- **استخدام المعالج**: > 80% ← توسع
- **استخدام الذاكرة**: > 85% ← توسع  
- **وقت الاستجابة**: > 1000 مللي ثانية ← توسع
- **معدل الخطأ**: > 5% ← تحقيق تلقائي

## 🔐 الأمان

### المصادقة

```python
from services import ConfigManager

config = ConfigManager()
jwt_secret = await config.get_config("security.jwt_secret")
```

### التشفير

```python
from services.core.config_manager import SecretManager

secret_manager = SecretManager()
secret_manager.store_secret("api_key", "مفتاح-سري")
decrypted = secret_manager.get_secret("api_key")
```

## 🧪 الاختبار

```bash
# اختبارات الوحدة
pytest services/tests/ --cov=services --cov-report=html

# اختبارات التكامل
pytest services/tests/integration/ -v

# اختبارات الأداء
pytest services/tests/performance/ --benchmark-only
```

## 📚 التوثيق

- [دليل الهندسة](./docs/architecture.md)
- [دليل التكوين](./docs/configuration.md)
- [دليل النشر](./docs/deployment.md)
- [مرجع API](./docs/api.md)

## 🛠️ التطوير

### المتطلبات المسبقة

- Python 3.9+
- Redis 6.0+
- Docker & Docker Compose
- Kubernetes (اختياري)

### متغيرات البيئة

```bash
AINFLUE_REDIS_URL=redis://localhost:6379
AINFLUE_LOG_LEVEL=INFO
AINFLUE_ENVIRONMENT=production
JWT_SECRET=سر-jwt-الخاص-بك
```

## 📞 الدعم

- **البريد الإلكتروني**: mlaiel@live.de
- **التوثيق**: [docs.ainflue.com](https://docs.ainflue.com)
- **الحالة**: [status.ainflue.com](https://status.ainflue.com)

## 📄 الترخيص

حقوق الطبع والنشر © 2025 فهد الملايل. جميع الحقوق محفوظة.

---

**المؤلف**: فهد الملايل (mlaiel@live.de)  
**الإصدار**: 1.0.0 للمؤسسات  
**آخر تحديث**: 7 يناير 2025