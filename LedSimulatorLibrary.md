Use the think tool to come up with a plan to implement this project.

The title of the library will be PyLEDSimulator

This project is to create a simulator of scrolling LED matrix hardware so that you can test your code easily in a debugger before getting it to run on the actual circuit python hardware.

The goal is to create a library that can be used as a base to simulate many different types of ESP 32 and other circuit python boards with attached LED displays. The sample implementation however, is for the MatrixPortal S3 from AdaFruit.

Be sure to separate out reusable functionality from the sample implementation of the MatrixPortal S3.  This sample with use a 64x32 LED display.

Look at the current implementation of a scrolling LED simulator and refactor to be used as a separate simulator library.  Keep the existing functionality, but create a self-contained PyLEDSimulator folder that can be hosted separately in github.

The simulated LED display library will use the Pygame library for the visual mockup of LED hardware.

The simulated display will mimic the pixels in an actual 64x32 display, using the higher resolution to render each individual LED. Do NOT simply render text using the higher resolution available in Pygame.

Although the sample code will use one display, implement code that will work for hardware devices with multiple LED displays that are combined to make larger displays.

To make sure that any CircuitPython code will render correctly in the simulator, it will be necessary to implement all methods in the displayio library.

Create a unit test for each re-implemented method in the displayio library, as well as for each piece of functionality in the new library.