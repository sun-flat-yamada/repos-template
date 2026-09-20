---
name: "toolchain-csharp"
description: "Executes .NET / C# development workflows including dotnet build, dotnet test, dotnet format, and Roslyn static analyzer inspections."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.cs"
  - "**/*.csproj"
  - "**/*.sln"
tags:
  - "skill"
  - "toolchain"
  - "csharp"
  - "build"
  - "test"
---
# Skill: C# Toolchain (`toolchain-csharp`)

## Instructions
1. **Restore & Build**:
   ```bash
   dotnet restore
   dotnet build --configuration Release --no-restore
   ```
2. **Format & Static Analysis**:
   ```bash
   dotnet format --verify-no-changes
   ```
3. **Automated Testing**:
   ```bash
   dotnet test --configuration Release --verbosity normal --collect:"XPlat Code Coverage"
   ```

## Best Practices
- Treat all compiler warnings as errors in CI pipeline.
- Verify nullability checks pass with zero warnings.
