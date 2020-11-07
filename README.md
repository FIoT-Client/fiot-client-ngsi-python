# FIoT-Client Python

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/105537359.svg)](https://zenodo.org/badge/latestdoi/105537359)

The FIoT-Client Python is a Python library that eases the use of IoT and Context APIs from FIWARE platform.

## Getting Started

<!--These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system. -->

### Prerequisites

Python 3.6+

<!--
What things you need to install the software and how to install them

```
Give examples
```
 -->

### Installing

You can install the latest stable version of the library from the Python package index, with the following command: 

```
pip install fiotclient
```

or install directly from the cloned repository folder:

```
cd fiot-client-python/
pip install -e .
```


<!--
A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo
-->

## Running the tests

To run the available unit tests, you should first configure a local FIWARE stack or use an external stack which you are granted access, so that the communication from the library to the FIWARE platform components can be tested.

[Here](https://github.com/FIoT-Client/fiot-client-tutorial/tree/master/deploy/full) you can find a *docker-compose* file that can be used to run a local instance of the required components.

Next, you should configure the *config.json* file, placed on **tests/file** folder with the configured FIWARE stack params (addresses and ports).

Finally, the tests can be executed using the following command:

```
python -m unittest
```

<!--
Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```
-->

## Deployment

<!--
Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds
-->

## Contributing

<!--
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.
-->

## Versioning

<!--
We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 
-->

## Authors

* **Lucas Cristiano Calixto Dantas** - *Initial work and developer*
* **Lucas Ramon Bandeira da Silva** - *Project collaborator*
* **Carlos Eduardo da Silva** - *Professor advisor*

<!--
See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.
-->

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

<!--
* Hat tip to anyone who's code was used
* Inspiration
* etc
-->
