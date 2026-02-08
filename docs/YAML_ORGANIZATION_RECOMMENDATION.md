# 📝 YAML Files Organization - Recommendation

## Current YAML Files in Your Project

### Found Files:
1. `config.yaml` (root) - Application configuration
2. `src/config/config.yaml` (duplicate) - Same file copied
3. `promptfoo-redteam.yaml` (root) - Testing configuration
4. `promptfooconfig.yaml` (root) - Testing configuration

---

## 🎯 My Recommendation: **Keep in Root** (with one exception)

### ✅ **KEEP in Root Directory:**

#### 1. **`promptfoo-redteam.yaml`** - KEEP in root
**Reason:** 
- Tool-specific configuration
- Promptfoo expects it in root
- Not part of your application code
- Used by external testing tool

#### 2. **`promptfooconfig.yaml`** - KEEP in root
**Reason:**
- Tool-specific configuration
- Promptfoo expects it in root
- Not part of your application code
- Used by external testing tool

### ⚠️ **MOVE to src/config/:**

#### 3. **`config.yaml`** - Already copied to `src/config/`
**Action:** DELETE the root copy, keep only `src/config/config.yaml`

**Reason:**
- Application configuration (not tool config)
- Should be with your source code
- Already have `settings.py` that loads it from `src/config/`
- Cleaner separation

---

## 📊 Recommended Final Structure

```
Medical-chatbot/
│
├── src/
│   └── config/
│       ├── config.yaml          ✅ Application config (KEEP)
│       └── settings.py           ✅ Config loader (KEEP)
│
├── promptfoo-redteam.yaml        ✅ Tool config (KEEP in root)
├── promptfooconfig.yaml          ✅ Tool config (KEEP in root)
│
└── Other root files...
```

---

## 🎯 Best Practices Explanation

### Application Config → `src/config/`
**Why:**
- Part of your application
- Loaded by your code
- Should be versioned with code
- Easy to find with source code

**Examples:**
- ✅ `config.yaml` - Your app settings
- ✅ `settings.py` - Config loader
- ✅ Any app-specific YAML configs

### Tool Config → Root Directory
**Why:**
- Expected by external tools
- Not part of your application code
- Tool looks for them in root
- Standard practice

**Examples:**
- ✅ `promptfooconfig.yaml` - Promptfoo tool
- ✅ `promptfoo-redteam.yaml` - Promptfoo tool
- ✅ `.github/workflows/*.yml` - GitHub Actions
- ✅ `docker-compose.yml` - Docker
- ✅ `.pre-commit-config.yaml` - Pre-commit hooks

---

## 🔧 Action Required

### Delete Duplicate:
```powershell
Remove-Item "config.yaml"  # Delete from root
```

**Keep only:** `src/config/config.yaml`

**Why:** 
- You already have `src/config/settings.py` that loads from `src/config/config.yaml`
- Having both creates confusion
- The root copy is now redundant

---

## 📋 Summary

| File | Location | Action | Reason |
|------|----------|--------|--------|
| `config.yaml` | Root | ❌ DELETE | Duplicate, use src/config/ version |
| `config.yaml` | src/config/ | ✅ KEEP | Application config |
| `promptfoo-redteam.yaml` | Root | ✅ KEEP | Tool expects it here |
| `promptfooconfig.yaml` | Root | ✅ KEEP | Tool expects it here |

---

## 💡 General Rule

**Application configs** → `src/config/`  
**Tool configs** → Root directory  
**CI/CD configs** → `.github/`, `.gitlab-ci.yml`, etc.  
**Container configs** → Root (`docker-compose.yml`, `Dockerfile`)  

---

## ✅ My Recommendation

1. **DELETE** `config.yaml` from root (it's a duplicate)
2. **KEEP** `src/config/config.yaml` (application config)
3. **KEEP** `promptfoo*.yaml` in root (tool configs)

This follows Python best practices and keeps your project clean!

**Would you like me to delete the duplicate `config.yaml` from root?**
