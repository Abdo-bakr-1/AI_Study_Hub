Review this entire project thoroughly before making any changes.

Your job is to act as a senior software engineer and perform a complete project audit.

Follow these steps:

1. Inspect the entire project structure and understand how the project works.
2. Read the important source files, configuration files, package files, database-related files, environment/configuration files, and documentation.
3. Identify any:

   * Bugs
   * Runtime errors
   * Build errors
   * Dependency conflicts
   * Incorrect configurations
   * Broken imports or references
   * Security issues
   * Authentication/authorization problems
   * Database issues
   * API issues
   * UI/UX problems that can cause broken functionality
   * Unused or duplicated code
   * Incorrect or outdated implementations
   * Missing error handling
   * Problems that may appear in production
4. Run the appropriate checks, tests, build commands, linters, type checks, and other verification commands available for this project.
5. Do not assume that the project is correct just because it runs. Verify the actual functionality.
6. For every issue you find, determine the root cause before fixing it.
7. Fix all issues you can safely fix yourself.
8. Do not rewrite or restructure working parts of the project unnecessarily.
9. Preserve the existing architecture, functionality, design, and intended behavior unless a change is required to fix a real problem.
10. Do not remove features just to make errors disappear.
11. If dependencies are outdated or conflicting, update them only when necessary and make sure the project remains compatible.
12. After making fixes, run the relevant checks again to verify that the fixes actually work.
13. Check for regressions caused by your changes.
14. Review the project one final time after all fixes.

Important:

* Work directly on the current project.
* Do not create a new project.
* Do not stop after finding the first error.
* Do not ask me to fix issues that you can safely fix yourself.
* If you encounter an issue that requires a decision from me, stop only for that specific issue and clearly explain what decision is needed.
* Never hide errors by disabling checks, deleting functionality, or using unsafe workarounds.
* Keep the code clean, maintainable, and production-ready.
* Do not modify secrets or expose API keys/passwords.
* Do not commit or push anything to Git unless I explicitly ask you to.

At the end, give me a concise report containing:

1. Problems found
2. Problems fixed
3. Files changed
4. Commands/tests executed
5. Remaining issues, if any
6. Whether the project is ready to run/build/deploy

Start by inspecting the project. Do not make assumptions before reviewing the code.
