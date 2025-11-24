export const Expression= ({text}: { text:any }) => (
    <span dangerouslySetInnerHTML={{ __html: `{{ ${text} }}`}} />
);

export const Trans = ({text} : {text: string} ) => (
    <span dangerouslySetInnerHTML={{ __html: `{% trans \"${text}\" %}`}} />
);

export const BlockTrans = ({text} : {text: string} ) => (
    <span dangerouslySetInnerHTML={{ __html: `{% blocktrans %}${text}{% endblocktrans %}`}} />
);

export const For = ({arrayName, iteratorName,children}: { arrayName: string, iteratorName:string, children:any }) => (
    <>
        <Expression text={`for ${iteratorName} in ${arrayName}`}/>
            {children}
        <Expression text={`endfor}`}/>
    </>
);

export const If = ({condition,children}: { condition: string, children:any }) => (
    <>
        <Expression text={`if ${condition}`}/>
            {children}
        <Expression text={`endif`}/>
    </>
);
