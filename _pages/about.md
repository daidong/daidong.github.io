---
permalink: /
title: ""
excerpt: "home"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

Dr. Dong Dai is an Assistant Professor in the [Computer Science Department](https://cci.charlotte.edu/computer-science/45/5) at [University of North Carolina at Charlotte](http://uncc.edu). Before joining UNCC, Dr. Dai has been working as a Research Assistant Professor at Texas Tech University, and previously PostDoc Researcher in a joint project between Texas Tech University and Argonne National Lab. He received his Doctor degrees in Computer Science from University of Science and Technology of China (USTC).

Dr. Dong Dai's research interests include a wide range of topics related to intelligent infrastructure for building and utilizing high-performance storage systems, including parallel file systems, metadata management, distributed graph storage, operating systems, and data-intensive machine learning infrastructure.

He is currently leading the [Data Intelligence Research (DIR) Lab](http://daidong.github.io/lab), a research group that focusing on co-designing data-intensive and inteligent systems. He is co-directing the Parallel and High-Performance Computing Lab in UNC-Charlotte.

<h2 id="News">News</h2>
 
 {% include base_path %}

{% for post in site.news reversed %}
  {% include archive-single.html %}
{% endfor %}

<h2 id="Research">Research Projects</h2>

{% include base_path %}

{% for post in site.projects reversed %}
  {% include archive-single.html %}
{% endfor %}

<h2 id="Publications">Recent and Selected Publications</h2>

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}

