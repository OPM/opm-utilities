Velocity Template Language  
--------------------------
   
The Velocity Template Language (VTL) is used to embed dynamic elements within what would otherwise be static templates. By using 
VTL it is possible to interact with the user, calculate values, incorporate conditional logic, and much more.                                                     
                                                                                                  
Directives
----------
Directives are script elements in the Velocity Template Language that can be used to manipulate the output generated by the 
Velocity engine.Brief summaries of the standard VTL directives are included below. For a more detailed description, refer to the 
Velocity User Guide on the Apache website.                                                                                          
                                                                                                  
Comment Directive  
-----------------
Like most programming languages, VTL includes constructs for inserting descriptive text comments into a template.Both single-line 
and multi-line (block) comments are supported. A single - line comment starts with  ## and only lasts until the end of the line. 
The following are examples of single-line comments:                                                                             
                                                                                                  
                            This is not a comment.  ## This is a comment                       
                            ## This whole line is a comment                                       
                                                                                                  
Multi-line comments are indicated by a start (  # *) and end comment indicator (*#).                
For example:                                                                                      
                                                                                                  
                           This text is outside of the comment block.It will be processed by the  
                           template engine                                                        
                           "#*                                                                     
                              This text is inside the comment block                               
                              Therefore it will be ignored by the template engine                 
                           *#"                                                                     
                           Back outside the comment block.This text will be processed             
                                                                                                  
Set Directive (#set)  
--------------------
One  of the most basic VTL directives is the  # set directive. It is used to assign a value to either a variable reference or a 
property reference. For example, the following are all valid # set statements:                                                                                 

                                      
                            $set ($ANS = "Yes")                                                     
                            #srt ($YeareStart = 2020)                                               
                                                                                                   
Conditional Directives(#if, #elseif, #else) 
-------------------------------------------
Velocity allows for the optional inclusion of text through the use of the conditional  #if directive. The statement is considered 
true if it is passed; that is a boolean variable whose value is true, an expression which evaluates to true, and an object which 
is not null. The following code illustrates these three cases:                                                     
                                                                                                  
                          #set ( $test = "true" )                           ## boolean variable   
                          #if ( $test )                                                           
                          This text is processed.                                                 
                          #end                                                                    
                                                                                                  
                          #if ($Year < $YearEnd)                            ## boolean expression 
                          $Year = $Year  1                                                       
                          #end                                                                    
                                                                                                  
                          #set ( $ANS = "Yes")                                                    
                          #if ( $Ans )                                       ## non-null object   
                          This text is processed.                                                 
                          #end"                                                                    
                                                                                                  
In addition, Velocty supports the logical AND ( & &), OR( | |) and NOT(!) operators, as well as standard relational operators  
such as equivalence( ==), greater than( >) and less than( <). Refer to the Velocity Users Guide for more information.                                                
                                                                                                  
Loop Directive (# foreach) 
--------------------------
The #foreach directive provides a way to loop over a template segment once for each object in a list of objects. For example, 
the following template code:                                        
                                                                                                  
                          #foreach ( $Year in [$YearStart .. $YearEnd] )                          
                          RPTSCHED                                                                
                          WELLS=2     WELSPECS      CPU=2      FIP=2                        /     
                                                                                                  
                          DATES                                                                   
                          1  JAN   $Year  /                                                       
                          /                                                                       
                                                                                                  
Include Directive (#include)
----------------------------
The # include directive is used to import a local file at the location where the #include directive is encountered. The contents 
of the file are not parsed by the template engine, but just included, for example:                                                                            
                                                                                                  
                          #include ("WCONPROD.vm")                                                
                          #include ("WCONINJE.vm")                                                
                                                                                                  
Parse Directive (#parse)   
------------------------
The #parse directive is similar to the #include directive, but rather than importing a static text file, the imported file is also 
parsed by the template engine, for example:                       
                                                                                                  
                          #include ("SCHEDULE.vm")                                                
                                                                                                  
Will parse all the directives in the SCHEDULE.vm template                                         
                                                                                                  
Stop Directive (#stop)  
----------------------
The #stop directive will halt template processing by the template engine. This is useful for debugging during template design.                                                                 
                                                                                                  
Macro Directive (#macro) 
------------------------
The #macro directive provides an easy method of defining repeated segments in a template. Here is a simple example:                                                                                 
                                                                                                  
                          #macro (datemacro)                                                      
                          This a Test Macro                                                       
                          #end                                                                    
The call to macro is:                                                                             
                          datemacro                                                               
                          datemacro                                                               
