// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Box {
    uint256 private value;

    event ValueChanged(uint256 newValue, uint256 oldValue);

    function store(uint256 _newValue) public {
        uint256 oldValue = value;
        value = _newValue;
        emit ValueChanged(value, oldValue);
    }

    function retrieve() public view returns (uint256) {
        return value;
    }
}
