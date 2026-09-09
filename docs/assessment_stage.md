Ways to assess the website further:

1 - **Manual Assessment:**  The best approach is to manually explore the website for any potential vulnerabilities by performing
a code review and manual testing.

2 - **Automated Tools:** Use security scanners and tools like:

<ul>
<li>mitmproxy</li>
It's only good for when you want to be the mitm in a secure connection. 

<li>W3AF</li>
It's good for automated vulnerability scanning such as SQLi, XSS, CSRF, Local/Remote File Inclusion.
The original repo is really old and not maintained anymore. It was written in Python 2.
There's <a href="https://github.com/mallaagency/w3af-python3">a fork</a> that tries to migrate it to Python 3.

<li>SQLmap</li>
Only use it if you know the target has a database layer (at least somewhere in its architecture).

<li>XSStrike</li>
Only focuses on Cross-Site Scripting (XSS) analysis.
I can't deny this library is more modern and relevant compared to other python cybersecurity libs I have studied so far, 
but the problem is that it only has a CLI interface and is not accessible through pure python code without using subprocess. 

<li>requests</li>
So far it's the best solution I have found for tergaet analyzation. But it's important to use it with custom payloads so you can perform
manual fuzzing and detect chances of custom injection. 

</ul>


