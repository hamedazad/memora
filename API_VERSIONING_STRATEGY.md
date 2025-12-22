# API Versioning & Deprecation Strategy

**Version:** 1.0.0  
**Last Updated:** 2025-01-12  
**Status:** Active

---

## 📋 Overview

This document outlines the API versioning strategy for **memora_core** backend and **memora_mobile** Flutter app to ensure smooth transitions, backward compatibility, and clear deprecation paths.

---

## 🎯 Versioning Approach

### Current Version
- **API Version:** v1
- **Base URL:** `/api/v1/`
- **Release Date:** 2024-01-01
- **Status:** Stable

### Versioning Strategy
We use **URL-based versioning** for major API changes:

```
/api/v1/memories/          # Current stable version
/api/v2/memories/          # Future major version (breaking changes)
```

---

## 🔢 Version Numbering

### Semantic Versioning for API

```
v{MAJOR}.{MINOR}.{PATCH}
```

- **MAJOR (v1 → v2):** Breaking changes requiring new base URL
- **MINOR (v1.0 → v1.1):** New features, backward compatible (same base URL)
- **PATCH (v1.0.0 → v1.0.1):** Bug fixes, fully backward compatible

### Examples

| Version | Type | Example Change | URL Change |
|---------|------|----------------|------------|
| v1.0.0 | Initial | First release | `/api/v1/` |
| v1.1.0 | Minor | Add new endpoints | `/api/v1/` (no change) |
| v1.1.1 | Patch | Fix bug in response | `/api/v1/` (no change) |
| v2.0.0 | Major | Remove deprecated endpoints | `/api/v2/` (new) |

---

## 🔄 Backward Compatibility Rules

### Must Maintain Compatibility
1. ✅ Adding new optional fields to request
2. ✅ Adding new fields to response
3. ✅ Adding new endpoints
4. ✅ Adding new query parameters (optional)
5. ✅ Adding new response status codes

### Breaking Changes (Require New Version)
1. ❌ Removing endpoints
2. ❌ Removing required fields
3. ❌ Changing field types (string → int)
4. ❌ Changing HTTP methods (GET → POST)
5. ❌ Changing response structure significantly
6. ❌ Removing or renaming fields in responses

---

## 📅 Deprecation Policy

### Deprecation Timeline

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Announce     │ Mark         │ Warn Users   │ Remove       │
│ Deprecation  │ Deprecated   │ Actively     │ Endpoint     │
│              │              │              │              │
│ Month 0      │ Month 1      │ Month 3      │ Month 6      │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Minimum Deprecation Period:** 6 months

### Deprecation Process

#### 1. Announce Deprecation (Month 0)
- Add to changelog
- Update API documentation
- Notify mobile team
- Create migration guide

#### 2. Mark Deprecated (Month 1)
- Add `deprecated: true` to OpenAPI schema
- Add response header: `X-API-Deprecated: true`
- Add response header: `X-API-Sunset: 2025-06-30`
- Log deprecation warnings

#### 3. Warn Users (Month 3)
- Send email notifications to API users
- Add deprecation notice to API docs homepage
- Display warnings in Swagger UI
- Update mobile app with migration path

#### 4. Remove Endpoint (Month 6)
- Remove from codebase
- Return `410 Gone` status for old endpoint
- Provide redirect to new endpoint when possible

---

## 🏷️ Deprecation Headers

### Response Headers for Deprecated Endpoints

```http
HTTP/1.1 200 OK
X-API-Deprecated: true
X-API-Sunset: 2025-06-30
X-API-Replacement: /api/v1/flutter/reminders/
Deprecation: @1735603200
```

### Client Handling

Mobile app should:
1. Log deprecation warnings
2. Display user notification (optional)
3. Track usage in analytics
4. Plan migration to new endpoint

---

## 📦 Current Deprecations

### Active Deprecations

| Endpoint | Deprecated | Sunset Date | Replacement | Reason |
|----------|-----------|-------------|-------------|--------|
| `/api/v1/smart-reminders/` | 2025-01-01 | 2025-07-01 | `/api/v1/flutter/reminders/` | Flutter-optimized endpoint |
| `/api/v1/smart-reminders/analyze/` | 2025-01-01 | 2025-07-01 | Automatic in create | Simplified flow |
| `/api/v1/smart-reminders/check/` | 2025-01-01 | 2025-07-01 | `/api/v1/flutter/reminders/check/` | Flutter-optimized |
| `/api/v1/smart-reminders/stats/` | 2025-01-01 | 2025-07-01 | `/api/v1/flutter/reminders/stats/` | Flutter-optimized |

### Migration Guide

#### From Legacy Smart Reminders to Flutter Endpoints

**Old Way (Deprecated):**
```dart
// DON'T USE - Deprecated
final response = await dio.get('/api/v1/smart-reminders/?memory_id=123');
```

**New Way (Recommended):**
```dart
// USE THIS - Flutter-optimized
final response = await dio.get('/api/v1/flutter/reminders/memory/123/');
```

**Benefits:**
- Better performance (optimized queries)
- Richer response data (includes memory details)
- Better error handling
- Consistent with Flutter patterns

---

## 🚀 Adding New Endpoints

### Checklist for New Endpoints

- [ ] Follow RESTful conventions
- [ ] Add OpenAPI schema annotations
- [ ] Write endpoint tests
- [ ] Update `API_ENDPOINT_MAPPING.md`
- [ ] Add to mobile `app_constants.dart`
- [ ] Document in Swagger UI
- [ ] Add to CHANGELOG
- [ ] Notify mobile team

### Naming Conventions

#### RESTful Endpoints
```
GET    /api/v1/memories/              # List all
POST   /api/v1/memories/              # Create new
GET    /api/v1/memories/{id}/         # Get specific
PUT    /api/v1/memories/{id}/         # Update full
PATCH  /api/v1/memories/{id}/         # Update partial
DELETE /api/v1/memories/{id}/         # Delete
```

#### Custom Actions
```
POST   /api/v1/memories/{id}/like/    # Custom action
POST   /api/v1/memories/{id}/share/   # Custom action
GET    /api/v1/memories/search/       # Collection action
```

#### Flutter-Optimized Endpoints
```
POST   /api/v1/flutter/memories/create/      # Optimized create
GET    /api/v1/flutter/reminders/check/      # Optimized check
```

---

## 📱 Mobile App Version Support

### Version Support Matrix

| Mobile App Version | Min Backend Version | Max Backend Version | Support Status |
|-------------------|--------------------|--------------------|----------------|
| 1.0.x | v1.0.0 | v1.9.x | ✅ Supported |
| 1.1.x | v1.1.0 | v1.9.x | ✅ Supported |
| 2.0.x | v2.0.0 | v2.9.x | 🔮 Future |

### Support Policy

- **Current Version:** Full support, all features
- **Previous Major Version:** Security fixes only for 12 months
- **Older Versions:** No support, must upgrade

---

## 🔐 Security Updates

### Critical Security Fixes

Security vulnerabilities are patched immediately:

1. Create hotfix patch version (e.g., v1.2.3 → v1.2.4)
2. Backport to all supported versions
3. Notify all users immediately
4. Force mobile app update if critical
5. Document in security advisory

### Example Response
```json
{
  "error": "critical_security_update_required",
  "message": "Please update to mobile app version 1.2.4 or later",
  "min_version": "1.2.4",
  "update_url": "https://memora.app/update"
}
```

---

## 📊 Version Checking

### Backend Version Endpoint

```http
GET /api/version/
```

**Response:**
```json
{
  "api_version": "v1",
  "server_version": "4.2.0",
  "min_mobile_version": "1.0.0",
  "latest_mobile_version": "1.2.5",
  "deprecated_endpoints": [
    "/api/v1/smart-reminders/"
  ],
  "sunset_dates": {
    "/api/v1/smart-reminders/": "2025-07-01"
  }
}
```

### Mobile Version Check

Mobile app should check version on startup:

```dart
final version = await apiService.checkVersion();
if (version.needsUpdate) {
  showUpdateDialog();
}
```

---

## 🧪 Testing Strategy

### Backward Compatibility Tests

```python
# tests/test_api_compatibility.py

def test_v1_endpoints_still_work():
    """Ensure v1 endpoints maintain backward compatibility"""
    # Test old request format still works
    response = client.post('/api/v1/memories/', {
        'content': 'Test memory',
        'memory_type': 'general'
    })
    assert response.status_code == 201
    
def test_deprecated_endpoints_return_headers():
    """Ensure deprecated endpoints return proper headers"""
    response = client.get('/api/v1/smart-reminders/')
    assert 'X-API-Deprecated' in response.headers
    assert 'X-API-Sunset' in response.headers
```

---

## 📝 Changelog Format

### CHANGELOG.md Structure

```markdown
# Changelog

## [v1.2.0] - 2025-01-15

### Added
- New `/api/v1/flutter/reminders/` endpoint for optimized reminder management
- Support for semantic search mode in `/api/v1/search/semantic`

### Changed
- Improved performance of `/api/v1/memories/` list endpoint
- Updated pagination to include `has_more` field

### Deprecated
- `/api/v1/smart-reminders/` - Use `/api/v1/flutter/reminders/` instead
  - Sunset date: 2025-07-15

### Fixed
- Fixed bug in date parsing for scheduled memories
- Fixed authentication token refresh issue

### Security
- Updated JWT token validation logic
- Added rate limiting to login endpoint
```

---

## 🎯 Best Practices

### Do's ✅
1. Version major breaking changes
2. Maintain backward compatibility within a version
3. Document all changes in CHANGELOG
4. Test compatibility thoroughly
5. Give users time to migrate (6+ months)
6. Use semantic versioning
7. Communicate changes early

### Don'ts ❌
1. Don't make breaking changes without new version
2. Don't remove endpoints without deprecation period
3. Don't change response structure without versioning
4. Don't surprise users with sudden changes
5. Don't skip deprecation warnings
6. Don't forget to update documentation

---

## 📞 Communication Channels

### Change Notifications

1. **Technical:** Update API documentation
2. **Email:** Send to registered API users
3. **In-App:** Display update prompts
4. **Website:** Post on developer blog
5. **GitHub:** Update CHANGELOG.md
6. **Slack:** Notify development team

---

## 🔮 Future Planning

### Planned Changes for v2.0.0

**Target Date:** Q3 2025

**Major Changes:**
1. Remove all deprecated v1 endpoints
2. Restructure response format for consistency
3. Implement GraphQL alongside REST
4. Add WebSocket support for real-time features
5. Improve error response format

**Migration Path:**
- 6-month overlap period
- Both v1 and v2 supported simultaneously
- Automatic migration tools provided
- Comprehensive migration guide

---

## 📚 References

- [REST API Design Best Practices](https://restfulapi.net/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Semantic Versioning](https://semver.org/)
- [API Deprecation Guide](https://nordicapis.com/api-versioning-methods-a-brief-reference/)

---

**Last Review:** 2025-01-12  
**Next Review:** 2025-04-12  
**Owner:** API Team































