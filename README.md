# fastbi ⚡️

**Scaffold Power BI projects instantly from templates.**

[![PyPI version](https://badge.fury.io/py/fastbi.svg)](https://pypi.org/project/fastbi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Create ready-to-use Power BI Projects (.pbip) with intelligent renaming and path updates—all from a single command.

---

<br>

![fastbi demo](https://media2.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MmhjOHBsYjZubzQ2czNhN3V5OWFqcW03ZWVucWRtaGhhNHVmMG42MSZlcD12MV9naWZzX3JlbGF0ZWQmY3Q9Zw/UiWG8AoIf4dtVEP4Bi/200.webp) 
*<p align="center">From template to working project in seconds.</p>*
<br>

## ✨ Quick Start

### Installation

**Option 1: Use without installing (quickest)**
```bash
uvx fastbi "My Project"
```

**Option 2: Install globally (recommended for frequent use)**
```bash
pip install fastbi

# Or with uv:
uv pip install fastbi
```

**Option 3: Run directly with uvx**
```bash
# No installation needed, runs in isolated environment
uvx fastbi "My Project"
```

### First-Time Setup

The first time you run fastbi, a setup wizard will ask for your `.pbip` template folder location.

![fastbi demo first time](https://s12.gifyu.com/images/b3b1a.gif)
*<p align="center">First time setup: uvx fastbi "My Project" prompts for template configuration.</p>*

```bash
# Try creating your first project - the wizard launches automatically
fastbi "My First Report"

# 🪄 The wizard will start:
# 🚀 Welcome! Let's configure your .pbip project template.
# Drag your template folder here and press Enter: _
```

### Create Projects

Once configured, just pass the project name:

![fastbi demo subsequent](https://s12.gifyu.com/images/b3b1Z.gif)
*<p align="center">Subsequent use: uvx fastbi "new project" creates a project without re-configuring the template.</p>*

```bash
# The main way (recommended):
fastbi "Q4 Sales Dashboard"

# ✓ Success! Project created at '202510 - Q4 Sales Dashboard'
```

**Multiple ways to create projects:**

```bash
# Shortcut (fastest):
fastbi "Annual Report"

# Explicit command:
fastbi create "Annual Report"
fastbi new "Annual Report"

# Using fbi alias (same functionality):
fbi "Annual Report"
```

<br>

## 🔧 How It Works

fastbi doesn't just copy files—it performs intelligent scaffolding:

- **🔍 Discovery**: Analyzes your `.pbip` template and automatically detects the base project structure
- **✏️ Rename**: Updates folder names, `.pbip` file, and `.Report`/`.SemanticModel` directories to match your new project
- **🔄 Update**: Edits internal JSON configs (`.pbip`, `.pbir`, `.platform`) so all paths and display names work correctly in Fabric

**Result:** Zero manual fixes. Your project just works.

<br>

## 🎨 Creating Your Template

The power of fastbi is that it works with **your own template**. Here's how:

1.  **Design Your Base Report**: Open Power BI Desktop and create your ideal starting point—add logos, themes, common pages, standard visuals.

2.  **Save as Project**: Go to `File > Save As`. In the file type dropdown, choose **`Power BI Project (*.pbip)`** instead of `.pbix`.

3.  **That's Your Template**: Power BI creates a folder with the project structure. Point the fastbi setup wizard to this folder.

> **Living Template**: Update your base report anytime. Just save it as `.pbip` again in the same location. All future projects will inherit the changes automatically.

<br>

## 🧰 Commands

| Command | Action |
| ------- | ------ |
| `fastbi "Name"` | Create a new project (shortcut) |
| `fastbi create "Name"` | Create a new project (explicit) |
| `fastbi new "Name"` | Create a new project (alias) |
| `fastbi setup` | Configure or reconfigure template path |
| `fastbi --help` | Show all commands and options |
| `fbi "Name"` | Same as fastbi, just cooler 😎 |

<br>

## 💡 Why fastbi?

- **Zero Config Needed**: Works with any `.pbip` template structure
- **Intelligent Updates**: Automatically fixes all internal paths and references
- **Date Prefixing**: Auto-adds `YYYYMM -` prefix to keep projects organized
- **Error Prevention**: Validates names and prevents overwrites
- **Multiple Aliases**: Use `fastbi`, `create`, `new`, or `fbi` - whatever fits your style

<br>

## 🚀 Advanced Usage

### Using with uv (recommended for speed)

```bash
# Install with uv (faster than pip)
uv pip install fastbi

# Or run without installing
uvx fastbi "Project Name"
```

### Reconfiguring Template

Need to change your template location?

```bash
fastbi setup
```

The wizard will guide you through selecting a new template folder.

<br>

## 📦 What Gets Created

When you run `fastbi "Sales Report"`, you get:

```
202410 - Sales Report/
├── Sales Report.pbip                    # Renamed project file
├── Sales Report.Report/                 # Renamed report folder
│   ├── definition.pbir                  # Updated with new paths
│   └── .platform                        # Updated display name
└── Sales Report.SemanticModel/          # Renamed model folder
    └── .platform                        # Updated display name
```

All internal references are automatically updated to match the new names.

<br>

## 🐛 Troubleshooting

**"No .pbip file found in template"**
- Make sure your template folder contains a `.pbip` file
- The template must be saved as Power BI Project format, not `.pbix`

**"Directory already exists"**
- A project with that name already exists for this month
- Choose a different name or delete the existing folder

**Commands not working?**
- Make sure you're using the latest version: `pip install --upgrade fastbi`
- For uvx users: `uvx --refresh fastbi "Project"`

<br>

## 🤝 Contributing

Issues and pull requests are welcome! Visit the [GitHub repository](https://github.com/AlejandroGonzalezColin/fastbi).

<br>

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for analysts and developers who value their time.**

*Forge your Power BI projects. Don't fight with folder structures.*
