import {
    Button,
    Hr,
    Section,
    Text,
} from '@react-email/components';

import BaseTemplate from "../components/baseTemplate";
import {BlockTrans, Expression, For, If, Trans} from "../components/jinja2";

export const VoteBody = () => (
    <BaseTemplate title="Title">
        <Section style={box}>
            <Text style={paragraph}>
                <Trans text={`You have successfully cast a vote in`}/> <br/>
            </Text>
            <code className="inline-block py-4 px-[4.5%] w-9/10 bg-[#f4f4f4] rounded-md border border-solid border-[#eee] text-[#333]">
                <Expression text={`election.name`} /><br/>
                <Expression text={`poll.name`} />
            </code>
            <Text style={paragraph}>
                <Trans text={`as`}/>
            </Text>
            <code className="inline-block py-4 px-[4.5%] w-9/10 bg-[#f4f4f4] rounded-md border border-solid border-[#eee] text-[#333]">
                <Expression text={`voter.voter_name`}/> <Expression text={`voter.voter_surname`}/> <br/>
                <Trans text={`with registration ID:`}/> <Expression text={`voter.voter_login_id`}/>
            </code>
            <Text style={paragraph}>
                <Trans text={`you can find your encrypted vote attached in this mail.`}/>
            </Text>
        </Section>
    </BaseTemplate>
);

export default VoteBody;


const box = {
    padding: '0 48px',
};

const hr = {
    borderColor: '#e6ebf1',
    margin: '20px 0',
};

const paragraph = {
    color: '#525f7f',

    fontSize: '16px',
    lineHeight: '24px',
    textAlign: 'left' as const,
};

const button = {
    backgroundColor: '#0A212F',
    borderRadius: '5px',
    color: '#fff',
    fontSize: '16px',
    fontWeight: 'bold',
    textDecoration: 'none',
    textAlign: 'center' as const,
    display: 'block',
    width: '100%',
    padding: '10px',
};
