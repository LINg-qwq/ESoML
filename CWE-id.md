# In CWE-1000 View

## 664 Improper Control of a Resource Through its Lifetime

- 400 Uncontrolled Resource Consumption
  - 770 Allocation of Resources Without Limits or Throttling
    - 774 Allocation of File Descriptors or Handles Without Limits or Throttling
    - 789 Memory Allocation with Excessive Size Value
    - 1325 Improperly Controlled Sequential Memory Allocation
  - 771 Missing Reference to Active Allocated Resource
    - 773 Missing Reference to Active File Descriptor or Handle
- 404 Improper Resource Shutdown or Release
  - 459 Incomplete Cleanup
    - 226  Sensitive Information in Resource Not Removed Before Reuse
      - 244 Improper Clearing of Heap Memory Before Release ('Heap Inspection')
    - 460 Improper Cleanup on Thrown Exception
  - 763 Release of Invalid Pointer or Reference
    - 761 Free of Pointer not at Start of Buffer
    - 762 Mismatched Memory Management Routines
      - 590 Free of Memory not on the Heap
  - 772 Missing Release of Resource after Effective Lifetime
    - 401 Missing Release of Memory after Effective Lifetime
    - 775 Missing Release of File Descriptor or Handle after Effective Lifetime
    - 1091 Use of Object without Invoking Destructor Method