# وثائق وحدة جمع البيانات

## نظرة عامة

توفر وحدة جمع البيانات (Collectors) بنية تحتية موحدة ومتطورة لمراقبة المحتوى على مستوى المؤسسات لمنصة Ainflue. تقوم هذه الوحدة بدمج 16 جامع بيانات فردي للمنصات في 6 جامعات بيانات منطقية مدمجة مع الحفاظ على التوافق مع الإصدارات السابقة.

## الهيكل المعماري

### الهيكل المدمج (المستوى 3 - أقصى عمق)

```
/backend/collectors/
├── __init__.py                    # تصدير الوحدة والتنسيق
├── base_collector.py              # أساس البنية التحتية
├── social_media_collector.py      # Instagram, TikTok, Twitter, Facebook, LinkedIn
├── video_platforms_collector.py   # YouTube, Twitch
├── community_collector.py         # Discord, Reddit
├── marketplace_collector.py       # Ecommerce, Pinterest
├── news_trends_collector.py       # News, Trends
├── miscellaneous_collector.py     # Misc + مصادر متخصصة
├── README.md                      # الوثائق (EN)
├── README.de.md                   # الوثائق (DE)
├── README.fr.md                   # الوثائق (FR)
└── README.ar.md                   # الوثائق (AR)
```

**إجمالي الملفات: 12** ✅ (يلبي المتطلبات)

## جامعات البيانات المدمجة

### 1. SocialMediaCollector
**المنصات**: Instagram, TikTok, Twitter, Facebook, LinkedIn

**الميزات**:
- البحث عبر المنصات
- مراقبة الهاشتاجات في الوقت الفعلي
- تحليل حضور المبدعين
- اكتشاف المحتوى الفيروسي
- تحليلات التفاعل

```python
from backend.collectors import SocialMediaCollector

collector = SocialMediaCollector({
    'instagram': {'api_key': 'مفتاحك'},
    'tiktok': {'api_secret': 'سرك'}
})

# البحث عبر جميع منصات التواصل الاجتماعي
results = await collector.search_content("محتوى المبدع", config)
```

### 2. VideoPlatformsCollector
**المنصات**: YouTube, Twitch

**الميزات**:
- مراقبة محتوى الفيديو
- اكتشاف البث المباشر
- تتبع نمو المبدعين
- تحليلات الأداء
- رؤى الربح

```python
from backend.collectors import VideoPlatformsCollector

collector = VideoPlatformsCollector({
    'youtube': {'api_key': 'مفتاحك'},
    'twitch': {'client_id': 'معرفك'}
})

# تتبع نمو المبدع
growth_data = await collector.track_creator_growth("creator_id", days=30)
```

### 3. CommunityCollector
**المنصات**: Discord, Reddit

**الميزات**:
- مراقبة نقاشات المجتمع
- اكتشاف ذكر العلامات التجارية
- تحليل المشاعر
- تتبع التفاعل
- تنبيهات فورية

```python
from backend.collectors import CommunityCollector

collector = CommunityCollector({
    'discord': {'bot_token': 'رمزك'},
    'reddit': {'client_id': 'معرفك'}
})

# مراقبة ذكر العلامات التجارية
mentions = await collector.monitor_brand_mentions(["اسم_العلامة"], config)
```

### 4. MarketplaceCollector
**المنصات**: Ecommerce, Pinterest

**الميزات**:
- تتبع أسعار المنتجات
- تحليل الاتجاهات البصرية
- فرص المبدعين
- رؤى السوق
- مراقبة الإيرادات

```python
from backend.collectors import MarketplaceCollector

collector = MarketplaceCollector({
    'ecommerce': {'api_key': 'مفتاحك'},
    'pinterest': {'access_token': 'رمزك'}
})

# العثور على فرص للمبدعين
opportunities = await collector.find_creator_opportunities("موضة", config)
```

### 5. NewsTrendsCollector
**المنصات**: News, Trends

**الميزات**:
- مراقبة الإعلام
- اكتشاف الاتجاهات
- تحليل مشاعر الأخبار
- رؤى القطاع
- تغطية العلامة التجارية

```python
from backend.collectors import NewsTrendsCollector

collector = NewsTrendsCollector({
    'news': {'api_key': 'مفتاحك'},
    'trends': {'access_token': 'رمزك'}
})

# تحليل مشاعر الأخبار
sentiment = await collector.analyze_news_sentiment("اسم العلامة", config)
```

### 6. MiscellaneousCollector
**المنصات**: مصادر متخصصة، APIs مخصصة، RSS feeds

**الميزات**:
- تكامل API مخصص
- مراقبة RSS feeds
- استخراج بيانات المواقع
- فرص المنصات
- التجميع عبر المنصات

```python
from backend.collectors import MiscellaneousCollector

collector = MiscellaneousCollector({
    'misc': {'custom_configs': 'إعداداتك'}
})

# مراقبة RSS feeds
rss_content = await collector.monitor_rss_feeds(["رابط_التغذية"], config)
```

## البنية التحتية الأساسية

### BaseCollector
فئة قاعدية مجردة توفر واجهة موحدة لجميع جامعات البيانات:

- تحديد معدل الطلبات
- إدارة الحالة
- جمع التحليلات
- معالجة الأخطاء
- مراقبة الأداء

### CollectorResult
هيكل نتائج موحد:

```python
@dataclass
class CollectorResult:
    platform: str
    content_id: str
    content_type: str
    title: str
    description: str
    url: str
    author: str
    timestamp: float
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]
    engagement_metrics: Optional[Dict[str, Any]]
    # ... حقول إضافية
```

## التكوين

### CollectionConfig
كائن التكوين لعمليات الجمع:

```python
@dataclass
class CollectionConfig:
    max_results: int = 50
    include_metadata: bool = True
    include_engagement: bool = True
    include_media: bool = False
    rate_limit_delay: float = 1.0
    timeout_seconds: int = 30
    retry_attempts: int = 3
```

## أمثلة الاستخدام

### البداية السريعة
```python
from backend.collectors import get_collector

# الحصول على جامع مدمج
social_collector = get_collector('social_media')

# الحصول على جامع منصة فردية (قديم)
instagram_collector = get_collector('instagram')

# قائمة المنصات المدعومة
platforms = get_supported_platforms()
```

### الاستخدام المتقدم
```python
from backend.collectors import (
    SocialMediaCollector, 
    VideoPlatformsCollector,
    CollectionConfig
)

# تهيئة جامعات البيانات
social = SocialMediaCollector()
video = VideoPlatformsCollector()

# تكوين الجمع
config = CollectionConfig(
    max_results=100,
    include_engagement=True,
    rate_limit_delay=2.0
)

# البحث عبر المنصات
social_results = await social.search_content("اسم المبدع", config)
video_results = await video.search_content("اسم المبدع", config)

# دمج النتائج
all_results = social_results + video_results
```

## الأداء والمراقبة

### تحديد معدل الطلبات
جميع جامعات البيانات تطبق تحديد معدل ذكي:
- حدود طلبات قابلة للتكوين
- تراجع تلقائي
- حدود خاصة بالمنصة
- إدارة الطلبات المتزامنة

### التحليلات
إحصائيات جمع مدمجة:
- معدلات النجاح/الفشل
- أوقات الاستجابة
- إجمالي الطلبات
- أداء المنصة

### إدارة الحالة
حالة جامع البيانات في الوقت الفعلي:
- IDLE, RUNNING, PAUSED, ERROR, COMPLETED
- مراقبة الصحة
- مقاييس الأداء

## دعم المبدعين

تدعم جامعات البيانات مراقبة شاملة للمبدعين:

### أنواع المبدعين
- **الموسيقيون**: YouTube Music، تكامل Spotify
- **المؤثرون**: وسائل التواصل الاجتماعي متعددة المنصات
- **المصورون**: التركيز على المنصات البصرية
- **المدونون**: مراقبة المحتوى النصي
- **البث المباشر**: تتبع المحتوى المباشر

### الميزات
- جمع محتوى متعدد الأشكال
- تحليلات عبر المنصات
- تتبع الإيرادات
- رؤى الجمهور
- مقاييس النمو

## حقوق الطبع والنشر والقانونية

### الملكية الفكرية
```
© 2025 فهد مليل - جميع الحقوق محفوظة

أي استخدام أو إعادة إنتاج أو تعديل أو توزيع أو تسويق
لهذا الكود أو المفهوم أو الفكرة بدون تصريح كتابي صريح
من فهد مليل محظور بشدة ويشكل انتهاكاً لحقوق الطبع والنشر
يخضع للملاحقة القضائية.

الاتصال للحصول على التصاريح: mlaiel@live.de
```

### المبدع والمالك
**فهد مليل** (mlaiel@live.de)
- المطور الرئيسي للذكاء الاصطناعي وهيكل جامعات البيانات
- مصمم نظام المراقبة متعدد المنصات
- المالك الحصري للملكية الفكرية

## المواصفات التقنية

### المتطلبات
- Python 3.8+
- دعم AsyncIO
- مكتبات عميل HTTP
- اتصال قاعدة البيانات
- Redis للتخزين المؤقت

### التبعيات
- aiohttp
- asyncio
- logging
- dataclasses
- typing
- datetime

### الأداء
- جمع متزامن عبر المنصات
- تحديد معدل ذكي
- هياكل بيانات فعالة في الذاكرة
- هيكل قابل للتوسع

## الدعم والاتصال

للدعم التقني أو طلبات الميزات أو استفسارات الترخيص:

**البريد الإلكتروني**: mlaiel@live.de  
**المنصة**: نظام مراقبة المبدعين Ainflue  
**الإصدار**: Enterprise v1.0  
**الترخيص**: ملكية خاصة - جميع الحقوق محفوظة