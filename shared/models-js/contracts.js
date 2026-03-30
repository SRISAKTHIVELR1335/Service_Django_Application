// Shared JS contracts for NIRIX Diagnostics
// These mirrors shared/api-contracts/schemas and are used by the Android client.

export const AuthUser = {
  id: 'number',
  email: 'string',
  name: 'string',
};

export const Vehicle = {
  id: 'number',
  name: 'string',
  code: 'string',
};

export const TestDefinition = {
  id: 'number',
  name: 'string',
  identifier: 'string',
  test_type: 'string',
  vehicle_id: 'number',
};

export const LogEntry = {
  id: 'number',
  vehicle_id: 'number',
  test_id: 'number',
  status: 'string',
  message: 'string',
};

export const VersionInfo = {
  id: 'number',
  version: 'string',
  vehicle_id: 'number',
};
