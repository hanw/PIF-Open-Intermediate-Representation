PIF Open IR: Experimental Framework
===================================

The pif_ir repository contains code related to experimentation with
intermediate representations.

PIF IR is a high level framework for describing network forwarding
processing logic and composing that logic into a functioning switch.


Overview
========
There is general Meta-IR code, which provides a framework for describing
IRs and simulating their behavior.  This is in the meta_ir subdirectory.

There is specific code for candidate IRs.  There are two experimental IRs:
- AIR : the original ("A") strawman, in the air subdirectory;
- BIR : the evolution ("B") from AIR, in the bir subdirectory.
BIR is the current active activity.

PIF IR uses YAML for its specifications, both for the metalanguage
specification of an IR and for the IR-particular specification of a
switch instance.

Each IR subdirectory notably contains a meta.yml file, which contains a
YAML description of the IR's object types and attributes, and is used
by the Meta-IR framework.  As an example, the following types are defined
in bir/bir_meta.yml:
- struct: a format for structured data
- metadata: a collection of data associated with each packet
- table: a lookup table managed by a control plane
- other_module: a library module supporting method calls
- basic_block: the unit of unconditional instruction execution
- control_flow: a processor which is a state machine traversing basic blocks
- other_processor: a library processor
- processor_layout: a data flow pipeline of processors

PIF IR has a simple Python-based switch simulator. It accepts an instance
of an IR-particular switch specification and instantiates
a switch conforming to the logic described.  It uses the OFTest framework
data plane implementation.  This allows the switch to use ethernet,
virtual ethernet, TCP sockets or UDP sockets as the port interfaces.

For detailed information, see the Doxygen generated documentation, and in
particular the readme files in the subdirectories.


Dependencies
============

The `pif_ir` source code is written in Python 2.7. The following packages are required to install and run the switch simulator:

- `pip`
- `pyyaml`
- `ply`

`pyyaml` and `ply` will be installed automatically by `setup.py` when installing the `pif_ir`.

Getting Started
============

This section assumes Ubuntu as the base install.

Install
----------

From the root directory (i.e. where `setup.py` is located) run:

    $ sudo pip install ./

Run Unit Tests
--------------
    $ cd pif_ir/bir/tests/
    $ make test

Run the BIR switch
------------------

    $ sudo scripts/veth_setup.sh
    $ cd pif_ir/examples/bir/
    $ make sample

To send packets to the switch use a separate terminal, and run:

    $ cd pif_ir/examples/bir/
    $ sudo ./send_udp_packets.py

