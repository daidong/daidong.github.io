---
title: "Undergraduate Research Initiative (ITCS 3050) - Fall 2023"
collection: teaching
type: "Undergraduate Course"
permalink: /teaching/2023-fall-uri
venue: "UNC-Charlotte, Computer Science Department."
date: 2023-05-01
location: "Charlotte, US"
---
# General Information

## 1. Why are we doing this?
We want to encourage our Undergraduate Students to participate in research as early as possible. So, we are looking for **Sophomore** and **Junior** students.

To you, this may be your first exposure to research! You can learn interesting techniques and get to know another career/education path!

## 2. Who is doing this?
Faculty members in the Computer Science Department, particularly Parallel High-Performance Computing Lab, are doing this. 

We are [Harini Ramaprasad](http://webpages.uncc.edu/hramapra/index.html), [Qiong Chen](go.charlotte.edu/qcheng1), [Tyler Allen](https://webpages.charlotte.edu/~tallen93/), [Dong Dai](http://daidong.github.io), [Erik Saule](https://webpages.charlotte.edu/~esaule/public-website/welcome.html), and [Yonghong Yan](https://passlab.github.io/yanyh/). Our Ph.D. students and we will be mentoring your research. 

In addition, Md. Hasanur Rashid (mrashid2@uncc.edu) will be our TA to interact with you during the semester.

## 3. How can I participate?
1. Spend 5-mins to fill this **[Google Form](https://forms.gle/mAtjeu8s2yAq8qsDA)** to Apply:  (Deadline **May. 2nd**).
2. Attend one of the in-person info sessions on **May 3** from 11:00am-12:00pm or 2:00pm-3:00pm.

**That is all!**

* We will contact you in later **May** via Zoom to learn more about your background and interests.
* We will register you in **Course ITCS 3050** in Fall 2023 for the program. 

## 4. How will the class go?
1. You will be matched to a research project.
2. You will work with specific faculty and group.
3. You will talk with Md. Hasanur Rashid (TA) biweekly to sync and complain.
4. We will host occasional seminar talks.
5. **Flexible class location, but Fixed Time**.
6. **We hired our URI students from 2023 Spring as RAs!**
7. Outcome of these projects include software artifacts and potential publications, which can be listed in your CV.

## 5. What are the Research Projects?
Our mentors are currently working on the list of research projects listed below (more are coming!). You will have the choice to pick the projects you are interested in and participate in. You can also propose your projects as long as your mentors agree.

### Project 1: Transforming Large-Scale Data Processing!
The large-scale programs run by supercomputers or dedicated corporate data centers, such as Google or Meta, are often bottlenecked not by computation, but by waiting for data to move between devices. At a small, single-computer scale, this problem is often solved prefetching data before it is required, such that the data is ready for processing before the computation requires it. These techniques are often too fine-grained and do not have sufficient foresight to predict coarser-grain data movement on large-scale devices. While there are many challenges to this problem at scale, we are interested in performing an exploratory investigation into using a transformer network, a deep learning technology featured in systems such as ChatGPT, to predict data requirements in advance and offset these huge data movement costs. This work has the long-term potential to improve the efficiency of large-scale data processing and save a tremendous amount of time and energy computing huge problems. Students working on this project will require a fluent understanding of Python, and have a basic understanding of how data moves through a computer architecture. Students would help with data collection, training, and evaluation of machine learning models.  

### Project 2: Scheduling Highly-Parallel Data Accesses!
Highly-Parallel processors, such as Graphics Processing Units (GPUs), are used to compute many of the world’s largest problems on modern computing systems. These problems range from climate simulation to artificial intelligence problems. The technology in these devices is advancing rapidly, now allowing first-class access to network and storage technologies. However, the software schedulers backing these devices are largely tuned towards much faster, sequential devices. By improving storage scheduling, we can reclaim large amounts of lost performance and make this technology viable for wider-scale use-cases. Students applying for this project will need to have an intermediate understanding of the C programming language and a basic understanding of storage devices and file systems. Students will help with analyzing scheduling bottlenecks, choosing new alternative strategies, and possibly implementing new scheduling algorithms.


### Project 3: Analysis and Visualization of Execution Tracing of Parallel Program!
Tracing the execution of parallel programs generates a large amount of data and it is often challenging to analyze tracing data for performance optimization. Existing approach, mostly known as profiling, which aggregates tracing data and metrics to provide an overall histogram summary of program execution, loses the dimensions of time-scale and parallel execution for performance analysis. In this project, we aim to develop Eclipse plugins for visualizing parallel program traces collected using LTTng. The plugin will use the Tracecompass framework, with SWT for 2-D and JavaFX for 3-D visualization. The goal is to provide more intuitive visualization and analysis methods for identifying performance bottlenecks of parallel programs. The implementation will also include the development of parallel calling context tree (PCCT), which is used to facilitate the attribution of performance problems to source code locations. 


### Project 4: Parallel Programming Models and Compiler based on OpenMP!
Parallel programming for heterogeneous architectures with complex memory systems requires dealing with multiple and hybrid parallelism patterns, ensuring efficient data transfer between different devices, and managing the complexity of memory hierarchies and synchronization. It also demands expertise in performance optimization techniques and the ability to adapt to rapidly evolving hardware and software ecosystems. In this project, we explore and develop existing and new programming paradigms and APIs for HPC and AI applications, and develop compiler support for new APIs and architectures. The development will be based on OpenMP, which we believe to be the most comprehensive parallel programming APIs, and we have a source-to-source compiler for C/C++/Fortran for the implementation of new features. The topics in this project include exploring new APIs for improving programmability of parallel programming, new compiler transformation techniques for supporting new architectures and APIs. 


### Project 5: Medical image processing using ML/DL!
Medical image processing using machine learning and deep learning faces challenges such as dealing with small datasets, complex image features, high computational requirements, and ensuring the interpretability and transparency of the models to enable clinicians to trust the results and make informed decisions. In this project, we will explore the use of MONAI deep learning framework for auto-segmentation of tumors and organs of MRI/PET/CT images, and of cells of pathology images. The development will include the implementation of ML/DL network and models in MONAI framework, exploring the usage of the framework for clinical applications, and evaluating the models and network for clinic settings for how to include DL in the clinical workflow and integrate with clinic applications. 


### Project 6: Visualization Site for Job Trace Analysis!
Amid the rising popularity of artificial intelligence (AI) and deep learning (DL) across various science domains, it is expected that high-performance computing (HPC) clusters will be increasingly utilized to host DL applications, rather than solely performing traditional numerical simulations. Not surprisingly, this new trend of cohabitation between DL workloads and numerical simulations within HPC systems will change the workload characteristics of the current systems, leaving many of the previously identified job characteristics obsolete or inaccurate. In this project, we will build a website with data analysis capabilities embedded in it so that various job traces can be easily analyzed and compared to reveal key insights about future job execution.


### Project 7: Job Trace Generator!
Designing new and evaluating job scheduling policies requires a large amount of high-fidelity job traces. However, these job traces are hard to collect. In this project, we will try to use machine learning methods, such as diffusion model, image reconstruction, and transformers to create high-fidelity job traces with the ‘style’ kept from one system to another.

### Project 8: Graph processing on a hierarchical memory system!
An enormous amount of unstructured data is being generated through different systems that the existing data pipelines cannot handle, especially within a limited timeline. For such a reason, graph processing has gained much attention in recent years due to its ability to model unstructured data. However, it is limited by the DRAM capacity of a single computing node. The emerging storage technologies, e.g., Persistent Memory (also known as PMEM), brings the potential features to overcome this limited memory challenge. PMEM can sit side by side with traditional memory (e.g., DRAM) and increase the overall memory capacity of computing systems. Specifically, with PMEM, we can now achieve up to 24TB of memory in a single computing node. With this large amount of memory, it is now possible to store and run analytics on large graphs in a single machine. However, this inclusion of PMEM makes the memory stack deeper than ever and brings us new opportunities. For example, data placement in this deep storage stack would be more challenging due to this new inclusion and vital for the application's performance. In this study, we want to investigate this problem for in-memory graph processing systems.

### Project 9: Large scale entity matching for theAdvisor
theAdvisor is a tool to help scholars find more papers relevant to their research. The system is built atop a complex dataset. The data come from various sources, DBLP, Microsoft Academic Graph, Citeseer, etc. The challenge is to take different datasets that fundamentally all describe the same papers and authors and match them together. Because of inaccuracies in the data, we need to use inexact matching algorithms based on hashing techniques. And because of the size of the data, we will need to deploy the methods atop a large scale data processing engine such as Map Reduce.
Ideal Knowledge: Python and C++

### Project 10: Visualizing real time performance of high performance applications
High performance applications are naturally hard for people to understand. The purpose of this project is to instrument a few existing high performance applications and prototypes so that the benefits of high performance computing become more apparent. We will add performance measurements in existing high performance codes, and stream these measurements to a web application for display.
Ideal Knowledge: Some C++, Some Python, Some Javascript, Some Linux.

### Project 11: Toolkit for educational knowledge graphs
An educational knowledge graph (EKG) is a type of knowledge graph that represents various educational entities, participants, resources, and their semantic relationships in a visual and interactive format. In AI-driven education, EKGs play a critical role in supporting teaching and learning by providing an integrative, dynamic, interconnected view of educational multifaceted information. However, the dynamic nature in education knowledge graph as well as the fact of its growing larger pose issues in its scalability and reliability, especially during its evolution.  In this undergraduate research project, we are going to measure the efficacy of different approaches in storing and inquiring educational knowledge graphs for reasoning and work toward designing a framework and developing a toolkit to construct and fuse knowledge graphs.

## Frequent Questions

### 0. Do I need to do a lot pre-studying for this course?

No, we will try to match your project to your skill background. You will mostly learn while working in the project.

### 1. Whether will multiple students be collaborating on the same project?

In most of the case, students will work with their mentors individually. It is OK to build a team though. 

### 2. Whether the students need to set up their own machines to work on the research project?

It depends on the project. In most of the cases, we will provide computing resources. PHPC lab hosts local clusters and also leverages [UNCC Research Computing facility](https://oneit.charlotte.edu/urc) to conduct research.

### 3. How will the course be structured?

* First 1-2 Weeks: Faculty members and Ph.D students introduce the projects. Students match with projects.
* During Semesters: Students work with their mentors during the semester via Weekly Meeting. There will be occational sessions to talk about specific topics, such as _How to use terminal_; _How to read a paper_; _How to prepare a poster_.
* Last 1-2 Weeks: There will be a poster/presentation session at the end of the semester.

### 4. How the workload looks on per weekly basis for the project?

The workload should be similar to a normal 3-credit UG course with the flexibility that you can move really fast at your pace.

### 5. Whether the student will need to deliver a final presentation?

Yes, there will be a poster/presentation session at the end of the semester.

### 6. Will the students get the chance to learn about relevant concepts before starting the project?

Yes, doing the project itself includes learning phase at beginining. 


# What are you waiting for? Fill this Google Form: [Link](https://forms.gle/mAtjeu8s2yAq8qsDA) (Deadline **May. 2nd**)
