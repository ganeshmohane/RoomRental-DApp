// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RentalContract {
    address public landlord;
    address public tenant;
    uint256 public monthlyRent;
    uint256 public securityDeposit;
    uint256 public rentalPeriod; // in months
    uint256 public startTimestamp;
    bool public isActive;

    constructor(uint256 _monthlyRent, uint256 _securityDeposit, uint256 _rentalPeriod) {
        landlord = msg.sender;
        monthlyRent = _monthlyRent;
        securityDeposit = _securityDeposit;
        rentalPeriod = _rentalPeriod;
        isActive = false;
    }

    modifier onlyLandlord() {
        require(msg.sender == landlord, "Only landlord can call this");
        _;
    }

    modifier onlyTenant() {
        require(msg.sender == tenant, "Only tenant can call this");
        _;
    }

    // Tenant deposits security and starts rental
    function startRental() public payable {
        require(!isActive, "Rental already active");
        require(msg.value == securityDeposit, "Must send exact security deposit");

        tenant = msg.sender;
        startTimestamp = block.timestamp;
        isActive = true;
    }

    // Pay monthly rent
    function payRent() public payable onlyTenant {
        require(isActive, "Rental not active");
        require(msg.value == monthlyRent, "Incorrect rent amount");
        require(block.timestamp < startTimestamp + rentalPeriod * 30 days, "Rental period has ended");

        payable(landlord).transfer(msg.value);
    }

    // End the rental, refund the security deposit
    function endRental() public onlyLandlord {
        require(isActive, "Rental not active");
        require(block.timestamp >= startTimestamp + rentalPeriod * 30 days, "Cannot end before rental period");

        isActive = false;
        payable(tenant).transfer(securityDeposit);
    }
}
