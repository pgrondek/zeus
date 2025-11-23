export const Trans = ({text} : {text: string} ) => (
    <div dangerouslySetInnerHTML={{ __html: `{% trans \"${text}\" %}`}} />
);

export const BlockTrans = ({text} : {text: string} ) => (
    <div dangerouslySetInnerHTML={{ __html: `{% blocktrans %}${text}{% endblocktrans %}`}} />
);

export default Trans;
