export const Expression= ({text}: { text:any }) => (
    <span dangerouslySetInnerHTML={{ __html: `{{ ${text} }} `}} />
);

export const Statement= ({text}: { text:any }) => (
    <span dangerouslySetInnerHTML={{ __html: `{% ${text} %}`}} />
);

export const Trans = ({text} : {text: string} ) => (
    <span dangerouslySetInnerHTML={{ __html: `{% trans \"${text}\" %}`}} />
);

export const BlockTrans = ({text} : {text: string} ) => (
    <span dangerouslySetInnerHTML={{ __html: `{% blocktrans %}${text}{% endblocktrans %}`}} />
);

export const For = ({arrayName, iteratorName,children}: { arrayName: string, iteratorName:string, children:any }) => (
    <>
        <Statement text={`for ${iteratorName} in ${arrayName}`}/>
            {children}
        <Statement text={`endfor`}/>
    </>
);

export const If = ({condition,children}: { condition: string, children:any }) => (
    <>
        <Statement text={`if ${condition}`}/>
            {children}
        <Statement text={`endif`}/>
    </>
);
