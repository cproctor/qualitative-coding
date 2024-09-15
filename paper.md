---
title: "A tool for qualitative data analysis designed to support computational thinking"
tags: 
 - qualitative data analysis
 - qualitative coding
 - computaitonal thinking
 - computational social science
 - python
authors: 
 - name: Chris Proctor
   orcid: 0000-0003-3492-9590
   affiliation: 1
affiliations: 
 - name: Graduate School of Education, University at Buffalo (SUNY), United States
   index: 1
date: 28 May 2024
bibliography: paper.bib
---

# Summary

`qc` is a free, open-source command-line-based tool for qualitative data 
analysis designed to support computational thinking. In addition to making the 
qualitative data analysis process more robust and efficient, computational thinking can 
contribute to the richness of subjective interpretation. The typical workflow
in qualitative research is an iterative cycle of "notice things," "think about 
things," and "collect things" [@seidel1998qualitative, p. 2]. `qc` provides
computational affordances for each of these practices, including the ability to 
integrate manual coding with automated coding, a tree-based hierarchy of codes
stored in a YAML file, allowing versioning of thematic analysis, and a powerful
query interface for viewing code statistics and snippets of coded documents. 

# Background

`qc` is designed to support the application of computational thinking
(CT) to qualitative data analysis (QDA). In the social
sciences, QDA is a method of applying codes to text, images, video, and
other artifacts, then analyzing the resulting patterns of codes and
using the codes to more deeply understand the text. 
When QDA is used in quantitative or mixed-methods research, it is
typically used to transform loosely-structured data such
as an interview transcript into categories or codes which can then be
used in downstream quantitative analysis answering predefined research
questions. In contrast, when QDA is used in qualitative research, 
it is typically part of an interpretive sensemaking process. These two uses
of QDA have been referred to as *little-q* ("looking for answers") and
*big-Q* ("looking for questions") qualitative research [@kidder1987].

The central design hypothesis of `qc` is that a closer partnership
between the researcher and the computational tool can enhance the
quality of QDA. This partnership, which could be characterized as 
augmented [@engelbart1962] or distributed cognition [@pea1997], depends on
the researcher's ability to conceptualize the data and the process in
computational terms, becoming immersed in the matrices, trees, and other
computational structures inherent to QDA rather than remaining "outside"
at the level of user interface. Such practices can be identified as *computational
thinking* (CT), "the thought processes involved in
formulating problems and their solutions so that the solutions are
represented in a form that can effectively be carried out by an
information-processing agent" [@wing2011research]. The application of CT to
QDA would mean conceptualizing the goal and the process of QDA in
computational terms, keeping a mental model of the work the computer is
doing for you.

# Statement of need

Although there are numerous well-known commercial QDA software 
packages such as NVivo [@dhakal2022nvivo], Dedoose [@salmona2019qualitative], 
Atlas.TI [@smit2002atlas], and MaxQDA [@kuckartz2010realizing], they do not 
provide affordances for users desiring more active engagement with the data and 
processes underlying QDA. `qc` better-supports such users, providing a scriptable 
command-line interface with powerful and flexible queries, wht data stored in simple 
and standardized formats. `qc` adopts the "unix philosophy" [@mcilroy1978] 
of building tools which do one thing well while being composable into 
flexible workflows, and the values of "plain-text social science" [@healy2020], emphasizing 
reproducability, transparency, and collaborative open science. 

`qc` was used in [@proctor2019] (described but not cited) and the author's 
doctoral dissertation; `qc` is currently a core tool supporting a large 
NSF-funded Delphi study [@ogbeifun2016delphi] involving multiple interviews 
with forty participant experts, open coding with over a thousand distinct 
codes, four separate coders, and several custom machine learning tools 
supporting the research team with clustering and synthesizing emergent themes.

# Acknowledgements

Development of `qc` was funded in part by a grant from the University at Buffalo's 
Digital Scholarship Studio Network. 

# References
