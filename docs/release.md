## Release process

This documents the process for issuing and deploying a new
release for CALC.

It assumes you want to create release `0.0.4`.

If this isn't the case, simply replace this value for your own. Or
alternatively, run `python manage.py releasehelp` to generate a
customized version of these instructions just for you.

To release version 0.0.4 of CALC:

1.  Verify that the ["Unreleased" section of `CHANGELOG.md`][unreleased]
    is up-to-date by comparing it against GitHub's commit list (you can
    see that by clicking on the "Unreleased" section heading), and then
    describe the changes in a human-meaningful form (see previous release
    entries for the appropriate level of human-friendliness).

    Feel free to move more important, less technical entries to the top
    of the list. Remember, it will be read by both developers *and* users,
    so avoid the use of jargon where possible.

2.  Create a branch off `develop` called `v0.0.4-rc` and push it to
    GitHub:

    ```
    git checkout -b v0.0.4-rc develop
    git push -u https://github.com/18F/calc.git v0.0.4-rc
    ```

3.  [Issue a PR][pr] to merge your branch into `master` titled
    "Tag and release v0.0.4". Paste in the latest changes from the
    topmost "Unreleased" section of `CHANGELOG.md` into the
    description of the PR so stakeholders know what's changed. If you're
    on OS X, you can easily copy this to your clipboard with the following
    command:

    ```
    python manage.py unreleased_changelog | pbcopy
    ```

4.  Make sure that all automated QA services (CircleCI, etc) think
    the PR looks good.

5.  Wait for the stakeholders to sign-off on the release.

6.  Update the version number in `hourglass/version.py` to `0.0.4` and then
    run:

    ```
    python manage.py bump_changelog
    ```

    This will create a new entry for the new version in `CHANGELOG.md`,
    and it will also output your new version's release notes to
    `tag-message-v0.0.4.txt`.

7.  Commit the changes to git and push them:

    ```
    git commit -a -m "Release v0.0.4."
    git push
    ```

8.  Merge the PR into `master` via the **Create a merge commit** merge
    strategy (i.e., do *not* squash or rebase). Once CircleCI is finished,
    the site will be deployed to staging.

9.  Visit the [staging instance][staging] and make sure all is functioning as
    expected.

10. Tag the release and push it to the official repository, which will trigger
    CircleCI to deploy the site to [production][production]:

    ```
    git tag -a v0.0.4 -F tag-message-v0.0.4.txt
    git push https://github.com/18F/calc.git v0.0.4
    ```

11. Merge `v0.0.4-rc` into `develop` on the official repository:

    ```
    git checkout develop
    git pull https://github.com/18F/calc.git develop
    git merge v0.0.4-rc
    git push https://github.com/18F/calc.git develop
    ```

Hooray, you're done!

[unreleased]: https://github.com/18F/calc/blob/develop/CHANGELOG.md#unreleased
[pr]: https://github.com/18F/calc/compare/master...v0.0.4-rc
[staging]: https://calc-staging.app.cloud.gov
[production]: https://calc.gsa.gov
