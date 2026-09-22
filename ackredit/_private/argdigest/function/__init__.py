"""Function argument contracts: what each public function accepts.

One module per function that takes `**kwargs`, because that is where the
contract is invisible to `inspect.signature`. A function with a closed
signature is held to its own parameters and needs nothing here.
"""
