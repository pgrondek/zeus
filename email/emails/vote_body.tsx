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
                <Trans text={`Legitimate recipient:`}/>
                <Expression text={`voter.voter_name`} />
                <Expression text={`voter.voter_surname`} />
            </Text>
        </Section>
        <Section style={box}>

            <Text style={paragraph}>
                <Trans text={`Dear voter,}`}/>
            </Text>
            <If condition={`custom_message`}>
                <Text style={paragraph}>
                    <Expression text={`custom_message|safe`} />
                </Text>
            </If>

            <Text style={paragraph}>
                <Trans text={`You are invited to vote in the poll:`}/>
            </Text>

            <code className="inline-block py-4 px-[4.5%] w-9/10 bg-[#f4f4f4] rounded-md border border-solid border-[#eee] text-[#333]">
                <Expression text={`election.name`} /><br/>
                <Expression text={`poll.name`} />
            </code>
            <Text style={paragraph}>
                <Trans text={`starting}`}/> <Expression text={`election.voting_starts_at`} />,
                <Trans text={`and ending}`}/> <Expression text={`election.voting_ends_at`} />
                <Trans text={`Your registration ID is:}`}/> <Expression text={`voter.voter_login_id`} />.
            </Text>

            <Text style={paragraph}>
                <Trans text={`To submit your vote, follow the link below}`}/>
            </Text>
            <Button style={button} href="{{ voter.get_quick_login_url }}">
                {`{ % trans "Vote now}`}
            </Button>

            <Hr style={hr}/>
            <Text style={paragraph}>
                <Trans text={`Information:}`}/>
            </Text>
            <ul>
                <li><Trans text={`You can vote more than once. Only your last vote will be counted.}`}/></li>
                <li>
                    <Trans text={`For information about the voting you can contact the trustees by phone,}`}/> <br/>
                    <Expression text={`election.help_phone`} /><br/>
                    <Trans text={`or by email,}`}/><br/>
                    <Expression text={`election.help_email`} /><br/>
                </li>
                <If condition={`voter.audit_passwords`} >
                    <li>
                        <Trans text={`If you want to initiate an audit vote,}`}/>
                        <Trans text={`the valid audit codes are}`}/>
                        <code
                            className="font-mono font-bold px-1 py-px bg-[#dfe1e4] text-[#3c4149] text-[21px] tracking-[-0.3px] rounded">
                            <For arrayName={`voter.get_audit_passwords`} iteratorName={`pass`}>
                                <Expression text={`pass`}/>
                            </For>
                        </code> <br/>
                        <Trans text={`Otherwise ignore those codes above.`} />
                    </li>
                </If>
            </ul>
            <Hr style={hr} />
            <Text style={paragraph}>
                {`Important:`}
            </Text>
            <Text style={paragraph}>
                <BlockTrans text={`Important:

The present message is strictly personal and confidential.
Do not forward or show it to others. Do not reply to this.`}/>
                <Trans text={`Instead, you can write to`}/>{`{{election.help_email}}.`}
                <BlockTrans text={`If you are not the legitimate recipient, please delete this message
and contact helpdesk@zeus.grnet.gr`}/>
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
