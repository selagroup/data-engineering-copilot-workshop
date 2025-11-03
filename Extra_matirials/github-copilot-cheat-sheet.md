# GitHub Copilot Workshop - Complete Cheat Sheet

> **Based on**: Official GitHub Copilot Documentation (October 2025)  
> **For**: VS Code on Windows with PowerShell

---

## 📋 Table of Contents
- [Module 1: Core Capabilities](#module-1-core-github-copilot-capabilities)
- [Module 2: Advanced Features](#module-2-advanced-copilot-features)
- [Module 3: Strategic Use](#module-3-strategic-use-of-copilot)
- [Keyboard Shortcuts](#keyboard-shortcuts-reference)
- [Command Palette Commands](#command-palette-commands-ctrlshiftp)
- [Chat Commands & Features](#chat-commands--features)
- [Best Practices](#best-practices)
- [Tutorials & Resources](#tutorials--resources)

---

## Module 1: Core GitHub Copilot Capabilities

### 🤖 What is GitHub Copilot
GitHub Copilot is an AI-powered coding assistant that provides:
- **Code Completions**: Inline suggestions as you type
- **Chat Interface**: Natural language conversations about code
- **Autonomous Coding**: AI-driven multi-file edits (Agent Mode)
- **Smart Actions**: AI-enhanced common developer tasks

**Plans Available:**
- **Copilot Free**: Limited monthly completions and chat interactions
- **Copilot Pro**: Extended features and higher limits
- **Copilot Pro+**: Premium models and advanced capabilities

---

### 💡 Contextual Suggestions (Code Completions)

**How it works:**
- Type code and Copilot suggests completions in ghost text
- Press `Tab` to accept suggestions
- Press `Esc` to dismiss

**Examples:**
```javascript
// Type: function calculateTax(
// Copilot suggests complete implementation

// Type: // Create a REST API endpoint for user authentication
// Copilot generates Express.js route code

const UserProfile = ({ // Copilot completes React component
```

**Best Practices:**
- Write descriptive comments before functions
- Use meaningful variable/function names
- Accept suggestions incrementally, don't blindly accept all

---

### 💬 Inline Chat (Fix, Explain, Optimize In-Place)

**Open Inline Chat:** `Ctrl+I`

**Use Cases:**
- **Fix**: Select code → `Ctrl+I` → "Fix the bug"
- **Explain**: Select code → `Ctrl+I` → "Explain this code"
- **Optimize**: Select code → `Ctrl+I` → "Optimize for performance"
- **Refactor**: Select code → `Ctrl+I` → "Refactor to use async/await"

**Inline Chat Features:**
- Works directly in the editor
- Context-aware (uses selected code)
- Applies changes in-place
- Supports follow-up questions

---

### 🗨️ Interactive Chat (Bigger Conversations, Context Window)

**Open Chat View:** `Ctrl+Alt+I`  
**Quick Chat:** `Ctrl+Shift+Alt+L`

**Chat Modes:**

| Mode | Shortcut | Use Case |
|------|----------|----------|
| **Ask** | Default | Ask questions, get explanations |
| **Edit** | Select from dropdown | Make controlled multi-file edits |
| **Agent** | Select from dropdown | Autonomous coding workflow |

**Chat View Features:**
- Persistent conversation history
- Multi-turn conversations
- Reference files, symbols, errors
- View model and context used
- Export chat sessions

---

## Module 2: Advanced Copilot Features

### 🔧 Extensions and Commands (/, #, @)

#### **@ Chat Participants**
Use `@` to invoke specialized assistants:

| Participant | Purpose | Example |
|-------------|---------|---------|
| `@workspace` | Codebase questions | `@workspace how does auth work?` |
| `@vscode` | VS Code help | `@vscode how to change theme?` |
| `@terminal` | Terminal commands | `@terminal how to list files?` |
| `@github` | GitHub operations | `@github search web for latest Node LTS` |

**GitHub Skills** (with `@github`):
- Web search: `@github #web What is the latest GPT model?`
- Code search: Ask naturally and Copilot selects the right skill

---

#### **# Chat Variables**
Use `#` to attach context:

| Variable | Purpose | Example |
|----------|---------|---------|
| `#file` | Reference a file | `Explain #file:app.py` |
| `#editor` | Active editor content | `Review #editor` |
| `#selection` | Selected code | `Optimize #selection` |
| `#codebase` | Entire codebase search | `Where is authentication in #codebase?` |
| `#terminalLastCommand` | Last terminal output | `Why did #terminalLastCommand fail?` |
| `#terminalSelection` | Terminal selection | `Explain #terminalSelection` |

---

#### **/ Slash Commands**
Use `/` for common actions:

| Command | Purpose |
|---------|---------|
| `/clear` | Clear conversation |
| `/new` | Start new conversation |
| `/tests` | Generate unit tests |
| `/fix` | Fix selected code |
| `/explain` | Explain code |
| `/doc` | Add documentation |

**Custom Commands** (from extensions):
- Extensions can add custom slash commands
- Type `/` to see all available commands

---

### 🧪 Unit Testing

**Generate Tests:**
1. Select function/class
2. Open Chat (`Ctrl+Alt+I`)
3. Type: `/tests` or "Generate unit tests for this function"
4. Copilot generates test cases with framework detection

**Run Tests:**
- Use VS Code Testing view
- Or command: `Testing: Run All Tests`

**Best Practices:**
- Provide context about test framework
- Specify edge cases in prompt
- Review generated tests for completeness

---

### 🛠️ Tools, Extensions, and MCP Servers

#### **Model Context Protocol (MCP)**
MCP servers extend Copilot with external capabilities.

**What are MCP Servers?**
- Standardized protocol for AI tool integration
- Run locally or remotely
- Provide specialized tools (databases, APIs, etc.)

**Built-in Tools:**
- `#fetch` - Retrieve web page content
- `#githubRepo` - Search GitHub repositories

**Using MCP Tools:**
```
# In Agent Mode or Chat:
Summarize #fetch code.visualstudio.com/updates
Find error handling in #githubRepo microsoft/vscode
```

**Configure MCP Servers:**
- Settings → Extensions → GitHub Copilot → MCP Servers
- Or via `settings.json`

**Popular MCP Servers:**
- Database connectors (PostgreSQL, MongoDB)
- API integrations
- Custom business logic

---

#### **VS Code Extensions for Copilot**
- **GitHub Copilot Chat**: Main extension
- **GitHub Copilot**: Code completions
- Install from Extensions Marketplace (`Ctrl+Shift+X`)

---

### 🔍 Code Review

**Request Code Review:**
1. Select code or open file
2. Press `Ctrl+Shift+P`
3. Type "Chat: Review" and press Enter
4. Or: Right-click → Copilot → Review

**Review Types:**
- Security vulnerabilities
- Performance issues
- Potentials Errors
- Best practices violations

**Using Custom Instructions for Reviews:**
- Create `.github/copilot-instructions.md`
- Specify coding standards
- Define review criteria

---

### 🌐 GitHub Copilot on GitHub.com

**Access Copilot Chat:**
1. Navigate to repository on GitHub.com
2. Click Copilot icon in file view
3. Ask questions about code, PRs, issues

**Features:**
- File-level explanations
- PR summaries
- Issue analysis
- Commit explanations

**GitHub Copilot Agents:**
- Assign Copilot to issues
- Creates PRs automatically
- Navigate: `github.com/copilot/agents`

**GitHub Copilot Spaces:**
- Collaborative AI workspace on GitHub.com
- Navigate: `github.com/copilot` or click Copilot icon in top bar
- Share context across team conversations
- Attach repositories, files, and issues
- Persistent chat sessions with history
- Use `@` mentions for repositories and team members
- Access MCP skills directly in the web interface

**Using Copilot Spaces:**
```
# Example prompts in Copilot Spaces:
Analyze security vulnerabilities in @owner/repo
Compare architecture between @repo1 and @repo2
Summarize changes in pull request #123
```

---

### 💻 GitHub Copilot Command Line

**New GitHub Copilot CLI:**
- Install npm install -g @github/copilot on your linux vm
- Natural language to shell commands
- Available via GitHub CLI

**Learn More:**
- [GitHub Copilot CLI Documentation](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)

---

## Module 3: Strategic Use of Copilot

### 🎯 Context is Everything

**Why Context Matters:**
- Better suggestions
- More accurate responses
- Fewer iterations

**Providing Context:**

1. **Use # Variables:**
   ```
   Fix the bug in #file:auth.py related to #selection
   ```

2. **Reference Multiple Files:**
   ```
   Compare authentication in #file:old-auth.js and #file:new-auth.ts
   ```

3. **Include Error Messages:**
   ```
   Why am I getting #terminalLastCommand error?
   ```

4. **Custom Instructions:**
   - Repository: `.github/copilot-instructions.md`
   - Path-specific: `.github/instructions/*.instructions.md`
   - Agent instructions: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`

**Custom Instructions Example:**
```markdown
---
applyTo: "**/*.py"
---
# Python Coding Standards
- Use type hints for all functions
- Follow PEP 8 style guide
- Prefer dataclasses over dictionaries
```

---

### 🐛 Debugging with Copilot

**Debugging Workflow:**

1. **Identify Error:**
   ```
   Explain this error: #terminalLastCommand
   ```

2. **Analyze Code:**
   ```
   Why is this function causing a memory leak? #selection
   ```

3. **Fix:**
   ```
   Fix the null reference error in #editor
   ```

4. **Verify:**
   ```
   Add error handling for edge cases
   ```

**Smart Actions for Debugging:**
- Always use Ask mode first
- When Looping through debugging the same problem - try asking copilot to "let's take a step back"
- Ask Copilot to add logging/debugging statements

**Debug View Integration:**
- Copilot can suggest breakpoint locations
- Explain watch expressions
- Generate test cases for failing scenarios

---

### ⚖️ Responsible Usage of AI

**Best Practices:**

1. **Review All Suggestions:**
   - Don't blindly accept code
   - Understand what's being generated
   - Test thoroughly

2. **Security Considerations:**
   - Review for vulnerabilities
   - Don't include secrets in prompts
   - Validate input handling

3. **Privacy:**
   - Copilot respects GitHub privacy settings
   - Enterprise data stays private
   - See [GitHub Copilot Trust Center](https://copilot.github.trust.page/)

4. **Copyright & Licensing:**
   - Be aware of code origins
   - Review license compatibility
   - Copilot trained on public repositories

5. **Quality:**
   - Use as assistant, not replacement
   - Apply code review standards
   - Maintain coding standards

6. **Transparency:**
   - Document AI-assisted code
   - Review references Copilot provides
   - Check "Used X references" in responses

---

## Keyboard Shortcuts Reference

### 🎹 Essential Shortcuts (Windows)

| Action | Shortcut |
|--------|----------|
| **Accept Inline Suggestion** | `Tab` |
| **Dismiss Suggestion** | `Esc` |
| **Open Inline Chat** | `Ctrl+I` |
| **Open Chat View** | `Ctrl+Alt+I` |
| **Quick Chat** | `Ctrl+Shift+Alt+L` |
| **Next Suggestion** | `Alt+]` |
| **Previous Suggestion** | `Alt+[` |
| **Trigger Suggestion** | `Alt+\` |

### 🔧 Chat Shortcuts

| Action | Shortcut |
|--------|----------|
| **New Chat** | `Ctrl+N` (in Chat view) |
| **Send Message** | `Enter` |
| **New Line in Prompt** | `Shift+Enter` |
| **Focus Chat Input** | `Ctrl+Alt+I` |
| **Show Chat History** | Click "Show Chats..." button |

### 📝 Smart Actions

| Action | How To |
|--------|--------|
| **Fix in Editor** | Select code → Right-click → Copilot → Fix |
| **Explain** | Select code → Right-click → Copilot → Explain |
| **Generate Docs** | Select code → Right-click → Copilot → Generate Docs |
| **Generate Tests** | Select code → Right-click → Copilot → Generate Tests |

---

## Command Palette Commands (Ctrl+Shift+P)

### 🎛️ Copilot Commands

Search for "Copilot" in Command Palette:

| Command | Purpose |
|---------|---------|
| `GitHub Copilot: Open Chat` | Open Chat view |
| `GitHub Copilot: Start Inline Chat` | Open inline chat |
| `GitHub Copilot: Enable/Disable` | Toggle Copilot on/off |
| `GitHub Copilot: Send to Chat` | Send selection to chat |
| `GitHub Copilot: Explain This` | Explain selected code |
| `GitHub Copilot: Fix This` | Fix selected code |
| `GitHub Copilot: Generate Docs` | Generate documentation |
| `GitHub Copilot: Generate Tests` | Generate unit tests |
| `Chat: Create Prompt` | Create reusable prompt file |
| `Chat: Show Chats...` | View chat history |
| `Chat: Export Chat...` | Export chat as JSON |
| `Developer: Show Chat Debug View` | See AI request/response details |

### 🔄 Chat Modes

| Command | Purpose |
|---------|---------|
| `Chat: Set Mode to Ask` | Switch to Ask mode |
| `Chat: Set Mode to Edit` | Switch to Edit mode |
| `Chat: Set Mode to Agent` | Switch to Agent mode |

---

## Chat Commands & Features

### 💬 Chat Modes Deep Dive

#### **Ask Mode**
- **Purpose**: Ask questions, get explanations
- **Behavior**: Provides code suggestions but doesn't auto-apply
- **Use When**: Learning, exploring, getting guidance

**Example Prompts:**
```
How does authentication work in this project?
What are the best practices for error handling in React?
Show me the differences between async/await and Promises
```

---

#### **Edit Mode**
- **Purpose**: Make controlled multi-file edits
- **Behavior**: You choose files (working set), Copilot proposes edits
- **Use When**: Specific, targeted changes across multiple files

**How to Use:**
1. Open Chat → Select "Edit" mode
2. Add files to working set
3. Describe changes: "Add error handling to all API calls"
4. Review and apply/discard per file

**Example Prompts:**
```
Add TypeScript types to all functions in working set
Refactor these components to use hooks
Update all imports to use new module path
```

---

#### **Agent Mode** ⭐
- **Purpose**: Autonomous coding workflow
- **Behavior**: AI determines files, runs commands, iterates on errors
- **Use When**: Complex tasks, new features, migrations

**How to Use:**
1. Open Chat → Select "Agent" mode
2. Describe task: "Create a user registration system with email verification"
3. Copilot plans, edits files, suggests terminal commands
4. Confirm or reject actions

**Example Prompts:**
```
Implement OAuth authentication using Passport.js
Migrate the codebase from JavaScript to TypeScript
Debug failing tests and apply fixes
Add a REST API for managing products with CRUD operations
```

**Agent Mode Tools:**
- Can invoke MCP servers
- Runs terminal commands (with permission)
- Iterates on errors automatically
- Uses extensions' tools

---

### 🗂️ Working Set (Edit/Agent Mode)

**Add Files to Working Set:**
- Click "+" in Chat view
- Drag files into chat
- Use `#file:path/to/file`

**Best Practices:**
- Keep working set focused (3-10 files)
- Include relevant context files
- Remove unnecessary files

---

### 📊 Language Models

**Change Model:**
- Click model picker in Chat view (bottom-right)
- Choose based on task:
  - **Fast models**: Quick suggestions, simple tasks
  - **Reasoning models**: Complex logic, planning
  - **Premium models**: Advanced capabilities (Copilot Pro+)

**Available Models** (varies by subscription):
- Claude Sonnet
- GPT-4o
- o1-preview
- o1-mini
- And more...

---

### 🖼️ Vision (Images in Chat)

**Supported Image Types:** JPEG, PNG, GIF, WEBP

**How to Use:**
1. Select vision-capable model
2. Drag/paste image into Chat view
3. Type prompt: "Explain this diagram"

**Use Cases:**
- Explain architecture diagrams
- Generate code from UI mockups
- Understand error screenshots
- Describe flowcharts

---

### 📜 Chat History & Checkpoints

**Chat History:**
- Each chat session is saved
- Access: "Show Chats..." button
- Export: Command Palette → "Chat: Export Chat..."

**Checkpoints** (Restore Previous State):
- VS Code creates snapshots during chat sessions
- Restore workspace to previous state
- Enable: `"chat.checkpoints.enabled": true`
- Restore: Hover over chat request → "Restore Checkpoint"

**Editing Previous Requests:**
- Click previous chat request to edit
- Settings: `"chat.editRequests": "inline"` (or `hover`, `input`)

---

### 🎤 Voice Interactions

**Requirements:**
- Install [VS Code Speech extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-speech)

**Features:**
- Dictate chat prompts
- "Hey Code" wake word
- Hold-to-speak mode

---

### 🪟 Chat in Separate Window

**Open Chat:**
- Chat view → `...` menu → "Open Chat in Editor"
- Or: "Open Chat in New Window"

**Benefits:**
- Multiple chat sessions
- Floating window (always on top)
- Compact mode

---

## Best Practices

### ✍️ Writing Effective Prompts

**Be Specific:**
❌ "Fix this"  
✅ "Fix the null pointer exception in the login function"

**Provide Context:**
❌ "Add validation"  
✅ "Add email validation to the user registration form, accepting standard formats"

**Iterate:**
- Start broad, refine based on results
- Ask follow-up questions
- Use "tell me more" or "show an example"

**Use Examples:**
```
Refactor this code to match the pattern used in #file:UserController.ts
```

---

### 🎯 Choosing the Right Tool

| Task | Recommended Tool |
|------|------------------|
| Quick code completion | Inline suggestions |
| Fix single issue | Inline Chat (`Ctrl+I`) |
| Ask a question | Chat View Ask Mode |
| Multi-file refactoring | Chat View Edit Mode |
| Build new feature | Chat View Agent Mode |
| Learn a concept | Chat View Ask Mode |
| Review code | Chat with `/review` or right-click → Review |
| Generate tests | Chat with `/tests` or right-click → Generate Tests |

---

### 🔒 Security & Privacy

**Do:**
- Review all generated code
- Scan for hardcoded secrets
- Validate input/output handling
- Use in private repos (protected by subscription)

**Don't:**
- Include API keys in prompts
- Paste sensitive data
- Skip code review for AI-generated code

**Learn More:**
- [GitHub Copilot Trust Center](https://copilot.github.trust.page/)
- [Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)

---

### 📚 Custom Instructions Best Practices

**Repository-Wide Instructions** (`.github/copilot-instructions.md`):
```markdown
# Project Overview
This is a React TypeScript project using Tailwind CSS.

## Coding Standards
- Use functional components
- Use arrow functions
- Always include TypeScript types
- Follow Airbnb ESLint config

## Testing
- Use Jest and React Testing Library
- Minimum 80% coverage
- Test user interactions, not implementation

## Build Commands
Always run `npm install` before building.
Build: `npm run build`
Test: `npm test`
Lint: `npm run lint`
```

**Path-Specific Instructions** (`.github/instructions/api.instructions.md`):
```markdown
---
applyTo: "src/api/**/*.ts"
---
# API Coding Standards
- Use async/await, not promises
- Always include error handling with try/catch
- Return typed responses
- Add JSDoc comments for all public functions
```

---

### 🧩 Prompt Files (Reusable Prompts)

**Enable:** Add to `.vscode/settings.json`:
```json
{
  "chat.promptFiles": true
}
```

**Create Prompt File:**
1. Command Palette → "Chat: Create Prompt"
2. Name it: `code-review.prompt.md`
3. Content:
```markdown
Review the following code for:
- Security vulnerabilities
- Performance issues
- Best practices violations
- Code smells

Provide specific recommendations with code examples.

Files to review:
#file:src/auth.ts
```

**Use Prompt:**
- Chat view → Click paperclip → "Prompt..." → Select your prompt

---

## Tutorials & Resources

### 📖 Official Documentation

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [VS Code Copilot Docs](https://code.visualstudio.com/docs/copilot)
- [GitHub Copilot Trust Center](https://copilot.github.trust.page/)

---

### 🎥 Video Tutorials

- [VS Code Copilot Series (YouTube)](https://www.youtube.com/playlist?list=PLj6YeMhvp2S5_hvBl2SE-7YCHYlLQ0bPt)
- Language-specific:
  - [Python](https://www.youtube.com/watch?v=DSHfHT5qnGc)
  - [C#](https://www.youtube.com/watch?v=VsUQlSyQn1E)
  - [Java](https://www.youtube.com/watch?v=zhCB95cE0HY)
  - [PowerShell](https://www.youtube.com/watch?v=EwtRzAFiXEM)

---

### 📘 Learning Paths

**Beginner:**
1. Set up Copilot in VS Code
2. Practice code completions
3. Try inline chat for simple fixes
4. Ask questions in Chat view

**Intermediate:**
5. Use Chat variables and participants
6. Create custom instructions
7. Try Edit mode for multi-file changes
8. Generate and run tests

**Advanced:**
9. Use Agent mode for complex tasks
10. Configure MCP servers
11. Create custom prompt files
12. Integrate Copilot into team workflow

---

### 🔗 Quick Links

- [Copilot Pricing](https://github.com/pricing)
- [VS Code Marketplace - Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- [GitHub Community Discussions](https://github.com/orgs/community/discussions)
- [Awesome Copilot Customizations](https://github.com/github/awesome-copilot)

---

### 🆘 Troubleshooting

**Copilot Not Working?**
1. Check status bar for Copilot icon
2. Verify subscription: GitHub Settings → Copilot
3. Sign out and sign back in: Command Palette → "GitHub: Sign Out"
4. Check network/proxy settings
5. Update VS Code and Copilot extension

**Getting Poor Suggestions?**
1. Provide more context with # variables
2. Write clearer comments
3. Use custom instructions
4. Try different language models
5. Refine prompts iteratively

**Authentication Issues?**
- Ensure you're signed into GitHub in VS Code
- Check organization permissions (if using Copilot Business)
- Clear VS Code credentials: Command Palette → "Developer: Clear Credentials"

---

### 💡 Pro Tips

1. **Use keyboard shortcuts** - Much faster than menus
2. **Combine @ and #** - `@workspace analyze #file:auth.py for security`
3. **Start sessions in Agent mode** for complex tasks
4. **Review references** - Click "Used X references" to see sources
5. **Create prompt files** for recurring tasks
6. **Use custom instructions** to enforce team standards
7. **Check Chat Debug View** to understand AI behavior
8. **Export important chats** for documentation
9. **Use Quick Chat** for one-off questions without losing focus
10. **Try different models** - Some work better for specific tasks

---

## 🎓 Workshop Exercises

### Module 1 Exercise:
- Enable Copilot in VS Code
- Accept 5 code completions
- Use inline chat to fix a bug
- Ask 3 questions in Chat view

### Module 2 Exercise:
- Use `@workspace` to understand a codebase
- Generate unit tests with `/tests`
- Configure a custom instruction file
- Try Edit mode for multi-file change

### Module 3 Exercise:
- Create debugging prompt with context
- Review code with custom standards
- Use Agent mode to build a feature
- Set up responsible AI guidelines for team

---

**Last Updated:** October 2025  
**Based On:** Official GitHub & VS Code Documentation  

---

*Happy Coding with GitHub Copilot! 🚀*
