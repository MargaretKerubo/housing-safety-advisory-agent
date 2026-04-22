module.exports = {
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'chore',
        'refactor',
        'docs',
        'style',
        'test',
        'perf',
        'build',
        'ci',
        'revert',
        'init',
        'config'
      ]
    ],
    'header-max-length': [2, 'always', 72],
    'subject-case': [2, 'never', ['upper-case']],
  },
};
