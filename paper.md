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
qualitative data analysis process more efficient, computational thinking can 
contribute to the richness of subjective interpretation. The typical workflow
in qualitative research is an iterative cycle of "notice things," "think about 
things," and "collect things" [@seidel1998qualitative, p. 2]. `qc` provides
computational affordances for each of these practices, including the ability to 
integrate manual coding with automated coding, a tree-based hierarchy of codes
stored in a YAML file, allowing versioning of thematic analysis, and a powerful
query interface for viewing code statistics and snippets of coded documents. 

# Statement of need

Qualitative data analysis, in its various forms, is a core methodology for 
qualitative, mixed methods, and some quantitative research in the social 
sciences. Although there are a variety of well-known commercial QDA software 
packages such as NVivo [@dhakal2022nvivo], Dedoose [@salmona2019qualitative], 
Atlas.TI [@smit2002atlas], and MaxQDA [@kuckartz2010realizing], they are generally 
designed to protect users from complexity rather than providing 
affordances for engaging with complexity via algorithms and data structures. 
The central design hypothesis of `qc` is that a closer partnership between
the researcher and the computational tool can enhance the quality of QDA.
`qc` adopts the "unix philosophy" [@mcilroy1978] of building tools which do 
one thing well while being composable into flexible workflows, and the 
values of "plain-text social science" [@healy2020], emphasizing 
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
