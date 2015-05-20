;;; eclipse.el --- major mode for ECLIPSE dot-DATA files
;;
;; $Id:$
;; 
;; Merged from Jan Rivenæs and Alf B. Rustad by Håvard Berland.
;;
;; Copyright (C) 2005-2014 Statoil
;; Copyright (C) 1997-2003 Eric M. Ludlam
;; Copyright (C) 1991-1997 Matthew R. Wette
;;
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 3, or (at your option)
;; any later version.

;;; Commentary:
;;
;; This major mode for GNU Emacs provides support for editing ECLIPSE dot-DATA
;; files.
;;
;; Current features includes colour coding for comment lines, and text in quotes.
;; Taylored menu in emacs, and key shortcuts, for (un)commenting regions.
;; Spellcheck for comments is implemented.
;; Navigation options for section/keyword is planned, as well as colour coding
;; for section headings and keywords. If wanted, the mode can be used for 
;; include files as well.
;;
;;; Installation:
;;
;; Put the this file as "eclipse.el" somewhere on your load path, then
;; add this to your .emacs or site-init.el file:
;;
;;   (autoload 'eclipse-mode "eclipse" "Enter ECLIPSE mode." t)
;;   (setq auto-mode-alist (cons '("\\.DATA\\'" . eclipse-mode) auto-mode-alist))
;;   (setq auto-mode-alist (cons '("\\.data\\'" . eclipse-mode) auto-mode-alist))
;;   (autoload 'eclipse-shell "eclipse" "Interactive ECLIPSE mode." t)
;;
;; To apply the mode to include files, you can add to the above, something like
;; the following:
;;   (setq auto-mode-alist (cons '("\\.INC\\'" . eclipse-mode) auto-mode-alist))
;;   (setq auto-mode-alist (cons '("\\.inc\\'" . eclipse-mode) auto-mode-alist))
;; depending on what extension you use for your include files.
;;
;;
;; This package requires easymenu, tempo, and derived.
;; This package will optionally use custom, shell, and gud.
;; This package supports language specific extensions in imenu, func-menu,
;;      speedbar, font-lock, and hilit19.

;;; Code:

(require 'easymenu)
(require 'tempo)
(require 'derived)

(defconst eclipse-mode-version "1.1"
  "Current version of ECLIPSE mode.")

;; From custom web page for compatibility between versions of custom:
(eval-and-compile
  (condition-case ()
      (require 'custom)
    (error nil))
  (if (and (featurep 'custom) (fboundp 'custom-declare-variable))
      nil ;; We've got what we needed
    ;; We have the old custom-library, hack around it!
    (defmacro defgroup (&rest args)
      nil)
    (defmacro custom-add-option (&rest args)
      nil)
    (defmacro defface (&rest args) nil)
    (defmacro defcustom (var value doc &rest args)
      (` (defvar (, var) (, value) (, doc))))))
;; compatibility
(if (string-match "X[Ee]macs" emacs-version)
    (progn
      (defalias 'eclipse-make-overlay 'make-extent)
      (defalias 'eclipse-overlay-put 'set-extent-property)
      (defalias 'eclipse-delete-overlay 'delete-extent)
      (defalias 'eclipse-overlay-start 'extent-start)
      (defalias 'eclipse-overlay-end 'extent-end)
      (defalias 'eclipse-cancel-timer 'delete-itimer)
      (defun eclipse-run-with-idle-timer (secs repeat function &rest args)
	(condition-case nil
	    (apply 'start-itimer
		   "eclipse" function secs
		   (if repeat secs nil) t
		   t args)
	  (error
	   ;; If the above doesn't work, then try this old version of
	   ;; start itimer.
	   (start-itimer "eclipse" function secs (if repeat secs nil)))))
      )
  (defalias 'eclipse-make-overlay 'make-overlay)
  (defalias 'eclipse-overlay-put 'overlay-put)
  (defalias 'eclipse-delete-overlay 'delete-overlay)
  (defalias 'eclipse-overlay-start 'overlay-start)
  (defalias 'eclipse-overlay-end 'overlay-end)
  (defalias 'eclipse-cancel-timer 'cancel-timer)
  (defalias 'eclipse-run-with-idle-timer 'run-with-idle-timer)
  )

(cond ((fboundp 'point-at-bol)
       (defalias 'eclipse-point-at-bol 'point-at-bol)
       (defalias 'eclipse-point-at-eol 'point-at-eol))
      ;; Emacs 20.4
      ((fboundp 'line-beginning-position)
       (defalias 'eclipse-point-at-bol 'line-beginning-position)
       (defalias 'eclipse-point-at-eol 'line-end-position))
      (t
       (defmacro eclipse-point-at-bol ()
	 (save-excursion (beginning-of-line) (point)))
       (defmacro eclipse-point-at-eol ()
	 (save-excursion (end-of-line) (point)))))

(defmacro eclipse-run-in-eclipse-mode-only (&rest body)
  "Execute BODY only if the active buffer is a ECLIPSE
M-file buffer."
  `(if (eq major-mode 'eclipse-mode)
       (progn
	,@body)
     (error "This command works only in a ECLIPSE M-file buffer.")))

(defun eclipse-with-emacs-link ()
  "Return non-nil if Emacs Link is running."
  (and (featurep 'eclipse-eei)
       eclipse-eei-process))

;;; User-changeable variables =================================================

;; Variables which the user can change
(defgroup eclipse nil
  "ECLIPSE mode."
  :prefix "eclipse-"
  :group 'languages)

;; Remove this when cursor-in-string and cursor-in-comment is fixed
(defcustom eclipse-elipsis-string "@£"
  "Text used to perform continuation on code lines.
This is used to generate and identify continuation lines.")

(defcustom eclipse-comment-line-s "-- "
  "*String to start comment on line by itself."
  :group 'eclipse
  :type 'string)

(defcustom eclipse-comment-on-line-s "-- "
  "*String to start comment on line with code."
  :group 'eclipse
  :type 'string)

(defcustom eclipse-comment-region-s "-- $$$ "
  "*String inserted by \\[eclipse-comment-region] at start of each line in \
region."
  :group 'eclipse
  :type 'string)


(defcustom eclipse-mode-hook nil
  "*List of functions to call on entry to ECLIPSE mode."
  :group 'eclipse
  :type 'hook)

(defvar eclipse-unterminated-string-face 'eclipse-unterminated-string-face
  "Self reference for unterminated string face.")

(defun eclipse-font-lock-adjustments ()
  "Make adjustments for font lock.
If font lock is not loaded, lay in wait."
  (if (and (featurep 'custom) (fboundp 'custom-declare-variable))
	
      (progn
	(defface eclipse-unterminated-string-face
	  (list
	   (list t
		 (list :background (face-background font-lock-string-face)
		       :foreground (face-foreground font-lock-string-face)
		       :underline t)))
	  "*Face used to highlight unterminated strings."
	  :group 'eclipse)
	)
      
    ;; Now, lets make the unterminated string face
    (cond ((facep 'font-lock-string-face)
	   (copy-face 'font-lock-string-face
		      'eclipse-unterminated-string-face))
	  (t
	   (make-face 'eclipse-unterminated-string-face)))
    (set-face-underline-p 'eclipse-unterminated-string-face t)
    )
)

;; Make the adjustments for font lock after it's loaded.
;; I found that eval-after-load was unreliable.
;;(if (featurep 'font-lock)
;;    (eclipse-font-lock-adjustments)
;;  (add-hook 'font-lock-mode-hook 'eclipse-font-lock-adjustments))
    
;;; ECLIPSE mode variables =====================================================

(defvar eclipse-tempo-tags nil
  "List of templates used in ECLIPSE mode.")


;;; Keybindings ===============================================================

(defvar eclipse-mode-map
  (let ((km (make-sparse-keymap)))
    (define-key km "\C-c;" 'eclipse-comment-region)
    (define-key km "\C-c:" 'eclipse-uncomment-region)
;;     (define-key km [(meta a)] 'eclipse-beginning-of-section)
;;     (define-key km [(meta e)] 'eclipse-end-of-section)
;;     (define-key km [(meta control a)] 'eclipse-beginning-of-keyword)
;;     (define-key km [(meta control e)] 'eclipse-end-of-keyword)
   km)
  "The keymap used in `eclipse-mode'.")

;;; Font locking keywords =====================================================
(defvar eclipse-string-start-regexp "\\(^\\|[^]})a-zA-Z0-9_.']\\)"
  "Regexp used to represent the character before the string char '.
The ' character has restrictions on what starts a string which is needed
when attempting to understand the current context.")

;; To quote a quote, put two in a row, thus we need an anchored
;; first quote.  In addition, we don't want to color strings in comments.
(defvar eclipse-string-end-regexp "[^'\n]*\\(''[^'\n]*\\)*'"
  "Regexp used to represent the character pattern for ending a string.
The ' character can be used as a transpose, and can transpose transposes.
Therefore, to end, we must check all that goop.")

(defun eclipse-font-lock-string-match-normal (limit)
  "When font locking strings, call this function for normal strings.
Argument LIMIT is the maximum distance to scan."
  (eclipse-font-lock-string-match-here
   (concat eclipse-string-start-regexp
	   "\\('" eclipse-string-end-regexp "\\)"
	   "\\([^']\\|$\\)")
   limit))

(defun eclipse-font-lock-string-match-unterminated (limit)
  "When font locking strings, call this function for normal strings.
Argument LIMIT is the maximum distance to scan."
  (eclipse-font-lock-string-match-here
   (concat eclipse-string-start-regexp "\\('[^'\n]*\\(''[^'\n]*\\)*\\)$")
   limit))

(defun eclipse-font-lock-string-match-here (regex limit)
  "When font-locking strings, call this function to determine a match.
Argument REGEX is the expression to scan for.  Match 2 must be the string.
Argument LIMIT is the maximum distance to scan."
  (let (e)
    (while (and (re-search-forward regex limit t)
		(progn
		  ;; This gets us out of a comment after the string.
		  (setq e (match-end 2))
		  (goto-char (match-beginning 2))
		  (prog1
		      (or (eclipse-cursor-in-comment)
			  (if (bolp) nil
			    (save-excursion
			      (forward-char -1)
			      (eclipse-cursor-in-string))))
		    (goto-char e))))
      (setq e nil))
    (if (not e)
	nil
      (goto-char e)
      t)))

(defun eclipse-font-lock-comment-match (limit)
  "When font-locking comments, call this function to determine a match.
Argument LIMIT is the maximum distance to scan."
  (let (e)
    (while (and (re-search-forward "\\(--[^\n]*\\)" limit t)
		(progn
		  (setq e (match-end 1))
		  (member (get-text-property (match-beginning 0) 'face)
			  '(font-lock-string-face
			    eclipse-unterminated-string-face))))
      (setq e nil))
    (if (not e)
	nil
      (goto-char e)
      t)))



(copy-face             'bold 'eclipse-font-lock-function-name-face)
(set-face-foreground         'eclipse-font-lock-function-name-face "Red")
(set-face-background         'eclipse-font-lock-function-name-face "Yellow")
(setq eclipse-font-lock-function-name-face 'eclipse-font-lock-function-name-face)

(copy-face             'bold 'eclipse-font-lock-keyword-face)
(set-face-foreground         'eclipse-font-lock-keyword-face "Blue")
(setq eclipse-font-lock-keyword-face 'eclipse-font-lock-keyword-face)

(defvar eclipse-font-lock-import-face nil "Import and Include")
(copy-face             'bold 'eclipse-font-lock-import-face)
(set-face-foreground         'eclipse-font-lock-import-face "DarkViolet")
(setq eclipse-font-lock-import-face 'eclipse-font-lock-import-face)

(defvar eclipse-font-lock-fnutt-face nil "Fnutt face")
(copy-face             'bold 'eclipse-font-lock-fnutt-face)
(set-face-foreground         'eclipse-font-lock-fnutt-face "Red")
(setq eclipse-font-lock-fnutt-face 'eclipse-font-lock-fnutt-face)

(defvar eclipse-font-lock-wfnutt-face nil "Word fnutt face")
(copy-face             'bold 'eclipse-font-lock-wfnutt-face)
(set-face-foreground         'eclipse-font-lock-wfnutt-face "ForestGreen")
(setq eclipse-font-lock-wfnutt-face 'eclipse-font-lock-wfnutt-face)

(copy-face             'font-lock-comment-face 'eclipse-font-lock-comment-face)
(set-face-foreground         'eclipse-font-lock-comment-face "DarkGoldenrod")
(setq eclipse-font-lock-comment-face 'eclipse-font-lock-comment-face)


(defconst ecl-font-lock-keywords
  (list
   '("/" . eclipse-font-lock-fnutt-face)
   '("/+.*$" . eclipse-font-lock-comment-face)
   '("[ ]*--+.*$" . eclipse-font-lock-comment-face)
   '("^--+.*$" . eclipse-font-lock-comment-face)
   '("\\b\\(^RUNSPEC\\|^EDIT\\|^GRID\\|^PROPS\\)\\b" . eclipse-font-lock-function-name-face)
   '("\\b\\(^SOLUTION\\|^REGIONS\\|^SUMMARY\\|^SCHEDULE\\)\\b" . eclipse-font-lock-function-name-face)
   '("^INCLUDE " . eclipse-font-lock-import-face)
   '("^INCLUDE$" . eclipse-font-lock-import-face)
   '("^IMPORT " . eclipse-font-lock-import-face)
   '("^IMPORT$" . eclipse-font-lock-import-face)
   ;; other keywords: all starts in first column and have large letters
   '("^[A-Z][A-Z0-9]*" . eclipse-font-lock-keyword-face)
   '("^[A-Z][A-Z0-9]* " . eclipse-font-lock-keyword-face)
   ;; words in '' keywords: all starts in first column and have large letters
   '("'[A-Z][A-Z0-9]*'" . eclipse-font-lock-wfnutt-face)
   '("'[A-Z][A-Z0-9]* *'" . eclipse-font-lock-wfnutt-face)
   ;; fnuttes
   ;;'("'" . eclipse-font-lock-fnutt-face)
   ;; numbers
   ;; '("'[0-9]*'" . eclipse-font-lock-wfnutt-face)
   )
"Expressions to highlight in ECL mode.")

;;; ECLIPSE mode entry point ==================================================

;;;###autoload
(defun eclipse-mode ()
  "ECLIPSE-mode is a major mode for editing ECLIPSE dot-DATA files.
Convenient editing commands are:
 \\[eclipse-comment-region]   - Comment/Uncomment out a region of code.
"
;; Convenient navigation commands are:
;;  \\[eclipse-beginning-of-section]   - Move to the beginning of a section.
;;  \\[eclipse-end-of-section]   - Move to the end of a section.
;;  \\[eclipse-beginning-of-keyword]   - Move to the beginning of a keyword.
;;  \\[eclipse-end-of-keyword]   - Move to the end of a keyword."

  (interactive)
  (kill-all-local-variables)
  (use-local-map eclipse-mode-map)
  (setq major-mode 'eclipse-mode)
  (setq mode-name "ECLIPSE")
  (if (boundp 'whitespace-modes)
      (add-to-list 'whitespace-modes 'eclipse-mode))

  (make-local-variable 'comment-start-skip)
  (setq comment-start-skip "--\\s-+")
  (make-local-variable 'comment-start)
  (setq comment-start "--")

  ;; Tempo tags
  (make-local-variable 'tempo-local-tags)
  (setq tempo-local-tags (append eclipse-tempo-tags tempo-local-tags))


;;   (make-local-variable 'font-lock-defaults)
;;   (setq font-lock-defaults '((ecl-font-lock-keywords
;; 			      )
;; 			     t ; do not do string/comment highlighting
;; 			     nil ; keywords are case sensitive.
;; 			     ))

  (setq font-lock-defaults '(ecl-font-lock-keywords))
  (font-lock-mode 1)



  (if window-system (eclipse-frame-init))
  (run-hooks 'eclipse-mode-hook)
)

;;; V19 stuff =================================================================

(defvar eclipse-mode-menu-keymap nil
  "Keymap used in ECLIPSE mode to provide a menu.")

(defun eclipse-frame-init ()
  "Initialize Emacs 19+ menu system."
  (interactive)
  ;; make a menu keymap
  (easy-menu-define
   eclipse-mode-menu
   eclipse-mode-map
   "ECLIPSE menu"
   '("ECLIPSE"
     ["Comment Region" eclipse-comment-region t]
     ["Uncomment Region" eclipse-uncomment-region t]
     "----"
;;      ("Navigate"
;;       ["Beginning of Section" eclipse-beginning-of-section t]
;;       ["End of Section" eclipse-end-of-section t]
;;       ["Beginning of Keyword" eclipse-beginning-of-keyword t]
;;       ["End of Keyword" eclipse-end-of-keyword t]
;;       ["Beginning of Record" eclipse-beginning-of-record t]
;;       ["End of Record" eclipse-end-of-record t])
     ["Spell check comments" eclipse-ispell-comments t]
;;     ["Check file" eclipse-check-file t] ;; TODO
     "----"
     ["Version" eclipse-show-version t]
))
  (easy-menu-add eclipse-mode-menu eclipse-mode-map)
)

;;; Comment management========================================================

(defun eclipse-comment ()
  "Add a comment to the current line."
  (interactive)
  (cond ((eclipse-ltype-empty)		; empty line
	 (eclipse-comm-from-prev)
	 (if (eclipse-lattr-comm)
	     (skip-chars-forward " \t--")
	   (insert eclipse-comment-line-s)
	   (eclipse-indent-line)))
	((eclipse-ltype-comm)		; comment line
	 (eclipse-comm-from-prev)
	 (skip-chars-forward " \t--"))
	((eclipse-lattr-comm)		; code line w/ comment
	 (beginning-of-line)
	 (re-search-forward "[^--]--[ \t]")
	 (forward-char -2)
	 (if (> (current-column) comment-column) (delete-horizontal-space))
	 (if (< (current-column) comment-column) (indent-to comment-column))
	 (skip-chars-forward "-- \t"))
	(t				; code line w/o comment
	 (end-of-line)
	 (re-search-backward "[^ \t\n^]" 0 t)
	 (forward-char)
	 (delete-horizontal-space)
	 (if (< (current-column) comment-column)
	     (indent-to comment-column)
	   (insert " "))
	 (insert eclipse-comment-on-line-s))))

(defun eclipse-comment-indent ()
  "Indent a comment line in `eclipse-mode'."
  (eclipse-calc-indent))

(defun eclipse-comment-region (beg-region end-region arg)
  "Comments every line in the region.
Puts `eclipse-comment-region-s' at the beginning of every line in the region.
BEG-REGION and END-REGION are arguments which specify the region boundaries.
With non-nil ARG, uncomments the region."
  (interactive "*r\nP")
  (let ((end-region-mark (make-marker)) (save-point (point-marker)))
    (set-marker end-region-mark end-region)
    (goto-char beg-region)
    (beginning-of-line)
    (if (not arg)			;comment the region
	(progn (insert eclipse-comment-region-s)
	       (while (and  (= (forward-line 1) 0)
			    (< (point) end-region-mark))
		 (insert eclipse-comment-region-s)))
      (let ((com (regexp-quote eclipse-comment-region-s))) ;uncomment the region
	(if (looking-at com)
	    (delete-region (point) (match-end 0)))
	(while (and  (= (forward-line 1) 0)
		     (< (point) end-region-mark))
	  (if (looking-at com)
	      (delete-region (point) (match-end 0))))))
    (goto-char save-point)
    (set-marker end-region-mark nil)
    (set-marker save-point nil)))

(defun eclipse-uncomment-region (beg end)
  "Uncomment the current region if it is commented out.
Argument BEG and END indicate the region to uncomment."
  (interactive "*r")
  (eclipse-comment-region beg end t))

;;; Semantic text insertion and management ====================================

(defun eclipse-ispell-strings-region (begin end)
  "Spell check valid strings in region with Ispell.
Argument BEGIN and END mark the region boundary."
  (interactive "r")
  (require 'ispell)
  (save-excursion
    (goto-char begin)
    ;; Here we use the font lock function for finding strings.
    ;; Its cheap, fast, and accurate.
    (while (and (eclipse-font-lock-string-match-normal end)
		(ispell-region (match-beginning 2) (match-end 2))))))

(defun eclipse-ispell-strings ()
  "Spell check valid strings in the current buffer with Ispell.
Calls `eclipse-ispell-strings-region'"
  (interactive)
  (eclipse-ispell-strings-region (point-min) (point-max)))

(defun eclipse-ispell-comments (&optional arg)
  "Spell check comments in the current buffer with Ispell.
Optional ARG means to only check the current comment."
  (interactive "P")
  (let ((beg (point-min))
	(end (point-max)))
  (if (and arg (eclipse-ltype-comm))
      (setq beg (save-excursion (eclipse-beginning-of-command) (point))
	    end (save-excursion (eclipse-end-of-command) (point))))
  (save-excursion
    (goto-char beg)
    (beginning-of-line)
    (while (and (eclipse-font-lock-comment-match end)
		(ispell-region (match-beginning 1) (match-end 1)))))))

;;; Navigation ===============================================================

(defvar eclipse-scan-on-screen-only nil
  "When this is set to non-nil, then forward/backward sexp stops off screen.
This is so the block highlighter doesn't gobble up lots of time when
a block is not terminated.")

;; Under construction
;; (defun eclipse-beginning-of-keyword ()
;;   "Go to the beginning of the current function."
;;   (interactive)
;;   (or (re-search-backward eclipse-keyword-regex nil t)
;;       (goto-char (point-min))))

;; (defun eclipse-end-of-keyword ()
;;   "Go to the end of the current function."
;;   (interactive)
;;   (or (progn
;; 	(if (looking-at eclipse-keyword-regex) (goto-char (match-end 0)))
;; 	(if (re-search-forward eclipse-keyword-regex nil t)
;; 	    (progn (forward-line -1)
;; 		   t)))
;;       (goto-char (point-max))))

;;; Line types and attributes =================================================

(defun eclipse-cursor-in-comment ()
  "Return t if the cursor is in a valid ECLIPSE comment."
  (save-match-data
    (save-restriction
      (narrow-to-region (eclipse-point-at-bol) (eclipse-point-at-eol))
      (save-excursion
	(let ((prev-match nil))
	  (while (and (re-search-backward
		       (concat "--\\|" (regexp-quote eclipse-elipsis-string) "+")
		       nil t)
		      (not (eclipse-cursor-in-string)))
	    (setq prev-match (point)))
	  (if (and prev-match (eclipse-cursor-in-string))
	      (goto-char prev-match))
	  (and (looking-at (concat "--\\|"
				   (regexp-quote eclipse-elipsis-string)))
	       (not (eclipse-cursor-in-string))))))))

(defun eclipse-cursor-in-string (&optional incomplete)
  "Return t if the cursor is in a valid ECLIPSE string.
If the optional argument INCOMPLETE is non-nil, then return t if we
are in what could be a an incomplete string."
  (let ((m (match-data))
	(returnme nil))
    (save-restriction
      (narrow-to-region (eclipse-point-at-bol) (eclipse-point-at-eol))
      (let ((p (1+ (point)))

	    (sregex (concat eclipse-string-start-regexp "'"))
	    (instring nil))
	(save-excursion
	  ;; Comment hunters need strings to not call the comment
	  ;; identifiers.  Thus, this routines must be savvy of comments
	  ;; without recursing to them.
	  (goto-char (point-min))
	  (while (or (and instring (looking-at "'"))
		     (and (re-search-forward
			   (concat "'\\|--\\|"
				   (regexp-quote eclipse-elipsis-string))
			   nil t)
			  (<= (point) p)
			  ;; Short circuit to fix this.
			  (progn (setq instring nil) t)))
	    ;; The next line emulates re-search-foward
	    (if instring (goto-char (match-end 0)))
	    (if (or (= -- (preceding-char)))
		;; Here we are in a comment for the rest of it.
		;; thus returnme is a force-false.
		(goto-char p)
		)))))
    (set-match-data m)
    returnme))
  

;;; Utilities =================================================================

(defun eclipse-check-file ()
  "Check Eclipse syntax, section headings, etc. Not done yet"
  (interactive)
  (message "eclipse-mode, version %s" eclipse-mode-version))


(defun eclipse-show-version ()
  "Show the version number in the minibuffer."
  (interactive)
  (message "eclipse-mode, version %s" eclipse-mode-version))


(provide 'eclipse)
