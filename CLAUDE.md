# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
* `make copy_to_circuitpy` - Deploy to MatrixPortal S3 device
* `make release` - Copy files to release archive

## Testing
* Run all tests: `make test-all` or `python -m pytest`
* Run unit tests only: `make test-unit` or `python -m pytest test/unit -v`
* Run legacy tests: `make test-legacy` or `python -m pytest test/test-suite.py -v`
* Run a single test: `python -m pytest test/unit/path/to/test_file.py::TestClass::test_method_name -v`
* Generate test coverage report: `make test-coverage` (requires pytest-cov)

### Test Organization
* Unit tests: `test/unit/` - organized by module (models, network, utils, etc.)
* Integration tests: `test/integration/` - tests for multiple components
* Legacy tests: `test/test-suite.py` - original test suite
* Test fixtures: `test/fixtures/` - test data files
* Helpers: `test/helpers.py` - testing utilities

### Test Tips
* Writing tests is difficult because CircuitPython is a subset of MicroPython, and many calls won't work when run on a computer. Also, the code that runs on the board expects hardware to be there.
* Use MagicMock() to stub out hardware component calls
* Use the MockHardwareContext from helpers.py when testing code that requires multiple hardware components
* Test fixtures in conftest.py provide access to common test data

## Code Style
* Think hard about how to find the root cause of problems. DO NOT cover up issues such as the lack of data.
* **Unit Tests**: Run all unit tests after each change.
* **Imports**: Group by stdlib, third-party (Adafruit), then project modules
* **Classes**: PascalCase (e.g., `ThemeParkList`)
* **Functions/Variables**: snake_case (e.g., `get_park_by_id`, `park_list`)
* **Constants**: UPPERCASE (e.g., `REQUIRED_MESSAGE`)
* **Error Handling**: Use try/except blocks with specific exceptions
* **Logging**: Use `ErrorHandler` class for centralized error logging
* **Documentation**: Use docstrings for classes and methods
* **Hardware Abstraction**: Include fallbacks when hardware components aren't available

## CircuitPython Development
* Instructions for the wait times API are at:  https://queue-times.com/pages/api
* All changes should be made to work on both the MatrixPortal S3 hardware and in the simulated dev environment. 
* The UI for the MatrixPortal hardware is in web_server.py and the UI for the development simulation is in dev_web_server.py.  Changes should always be made to both files. 
* Remember that CircuitPython 3.x is a fork of MicroPython, and the standard libraries either aren't available or have versions specific to CircuitPython
* CircuitPython devices are very slow and have use cooperative multitasking using asyncio, not multithreading. This is made more difficult because the CircuitPython HTTP library is synchronous, so background tasks like scrolling stop when HTTP calls are made. 
* Support both running on actual hardware and testing in standard Python environment
* Run all unit tests after every code change.  Iterate until all of the tests pass.
* Test functionality in isolation before deploying to hardware
* Ensure tests properly mock CircuitPython-specific modules
* Separate functionality that could be applied to any CircuitPython project from the specific functionality of this project. The ultimate goal is to refactor into an open source library.

## Using the think tool
Before taking any action or responding to the user after receiving tool results, use the think tool as a scratchpad to:
- List the specific rules that apply to the current request
- Check if all required information is collected
- Verify that the planned action complies with all policies
- Iterate over tool results for correctness

Here are some examples of what to iterate over inside the think tool:
<think_tool_example_1>
User wants to cancel flight ABC123
- Need to verify: user ID, reservation ID, reason
- Check cancellation rules:
    * Is it within 24h of booking?
    * If not, check ticket class and insurance
- Verify no segments flown or are in the past
- Plan: collect missing info, verify rules, get confirmation
  </think_tool_example_1>

<think_tool_example_2>
User wants to book 3 tickets to NYC with 2 checked bags each
- Need user ID to check:
    * Membership tier for baggage allowance
    * Which payments methods exist in profile
- Baggage calculation:
    * Economy class × 3 passengers
    * If regular member: 1 free bag each → 3 extra bags = $150
    * If silver member: 2 free bags each → 0 extra bags = $0
    * If gold member: 3 free bags each → 0 extra bags = $0
- Payment rules to verify:
    * Max 1 travel certificate, 1 credit card, 3 gift cards
    * All payment methods must be in profile
    * Travel certificate remainder goes to waste
- Plan:
1. Get user ID
2. Verify membership level for bag fees
3. Check which payment methods in profile and if their combination is allowed
4. Calculate total: ticket price + any bag fees
5. Get explicit confirmation for booking
   </think_tool_example_2>