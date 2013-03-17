##!/usr/bin/env python
## coding=utf-8
## Author:  vavava
#
#
#import tesseract4py,os
#"""
#    enum OcrEngineMode {
#        OEM_TESSERACT_ONLY,         // Run Tesseract only - fastest
#        OEM_CUBE_ONLY,              // Run Cube only - better accuracy, but slower
#        OEM_TESSERACT_CUBE_COMBINED,// Run both and combine results - best accuracy
#        OEM_DEFAULT                 // Specify this mode when calling init_*(),
#                                    // to indicate that any of the above modes
#                                    // should be automatically inferred from the
#                                    // variables in the language-specific config,
#                                    // command-line configs, or if not specified
#                                    // in any of the above should be set to the
#                                    // default OEM_TESSERACT_ONLY.
#    };
#    """
#"""
#enum PageSegMode {
#  PSM_OSD_ONLY,       ///< Orientation and script detection only.
#  PSM_AUTO_OSD,       ///< Automatic page segmentation with orientation and
#                      ///< script detection. (OSD)
#  PSM_AUTO_ONLY,      ///< Automatic page segmentation, but no OSD, or OCR.
#  PSM_AUTO,           ///< Fully automatic page segmentation, but no OSD.
#  PSM_SINGLE_COLUMN,  ///< Assume a single column of text of variable sizes.
#  PSM_SINGLE_BLOCK_VERT_TEXT,  ///< Assume a single uniform block of vertically
#                               ///< aligned text.
#  PSM_SINGLE_BLOCK,   ///< Assume a single uniform block of text. (Default.)
#  PSM_SINGLE_LINE,    ///< Treat the image as a single text line.
#  PSM_SINGLE_WORD,    ///< Treat the image as a single word.
#  PSM_CIRCLE_WORD,    ///< Treat the image as a single word in a circle.
#  PSM_SINGLE_CHAR,    ///< Treat the image as a single character.
#
#  PSM_COUNT           ///< Number of enum entries.
#};
#"""
#
##for mode
#OEM_TESSERACT_ONLY            = 0
#OEM_CUBE_ONLY                 =1
#OEM_TESSERACT_CUBE_COMBINED   =2
#OEM_DEFAULT                   =3
##for seg mode
#PSM_OSD_ONLY                 = 0
#PSM_AUTO_OSD                 = 1
#PSM_AUTO_ONLY                = 2
#PSM_AUTO                     = 3
#PSM_SINGLE_COLUMN            = 4
#PSM_SINGLE_BLOCK_VERT_TEXT   = 5
#PSM_SINGLE_BLOCK             = 6
#PSM_SINGLE_LINE              = 7
#PSM_SINGLE_WORD              = 8
#PSM_CIRCLE_WORD              = 9
#PSM_SINGLE_CHAR              = 10
#PSM_COUNT                    = 11
#
#class Tesseract4py:
#    def __init__(self,path,lang="eng",config="letters",
#             mode=OEM_TESSERACT_CUBE_COMBINED, seg_mode=PSM_SINGLE_LINE):
#        self.path = path
#        self.lang = lang
#        self.config = config
#        self.mode = mode
#        self.seg_mode = seg_mode
#
#    def img_to_string(self,image):
#        return tesseract4py.img2str(image,self.path,
#            self.lang,self.config,self.seg_mode, self.mode)
#
#if __name__ == "__main__":
#    image = r'D:\_code\online\trunk\python\Src\test\pic\12.png'
#    path  = r'D:\_code\online\trunk\python\Src\tracker\spiders\tessdata'
#    lang  = r'eng'
#    config = r'D:\_code\online\trunk\python\Src\tracker\spiders\tessdata\configs\letters'
#    tess = Tesseract4py(path=path,lang=lang)
#    re = tess.img_to_string(image)
#    if re:
#        print(re)
#
