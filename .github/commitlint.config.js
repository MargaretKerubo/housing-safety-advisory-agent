module.exports = {
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'fix',        // Bug fix
        'feat',       // New feature / Enhancement
        'refactor',   // Refactor
        'docs',       // Documentation
        'ci',         // CI changes
        'build',      // Build changes
        'config'      // Config changes
      ]
    ],
    'header-max-length': [2, 'always', 72],
    'subject-case': [2, 'never', ['upper-case']],
    'type-case': [2, 'always', 'lower-case'],
  },
};
